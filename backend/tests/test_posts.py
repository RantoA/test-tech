from collections.abc import Callable
from typing import Any

from fastapi.testclient import TestClient

from app.config.settings import settings
from tests.conftest import API, csrf_headers, make_image, post_form

CreatePost = Callable[..., dict[str, Any]]


def _stored_files(upload_dir) -> set[str]:
    return {p.name for p in upload_dir.iterdir()} if upload_dir.exists() else set()


# ---- create -----------------------------------------------------------------------------


def test_create_post_without_image(auth_client: TestClient) -> None:
    response = auth_client.post(f"{API}/posts", data=post_form(), headers=csrf_headers(auth_client))
    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "Post created successfully"
    post = body["data"]
    assert post["title"] == "My first post"
    assert post["slug"] == "my-first-post"
    assert post["cover_image"] is None
    assert post["cover_image_url"] is None
    assert post["author"]["name"] == "Alice Martin"
    assert [block["type"] for block in post["content"]] == ["heading", "subheading", "paragraph"]


def test_create_post_with_image(create_post: CreatePost, client: TestClient, upload_dir) -> None:
    post = create_post(image=make_image("PNG"))
    assert post["cover_image"].endswith(".png")
    assert post["cover_image_url"].endswith(f"/uploads/{post['cover_image']}")
    assert post["cover_image"] in _stored_files(upload_dir)

    served = client.get(f"/uploads/{post['cover_image']}")
    assert served.status_code == 200
    assert served.headers["content-type"] == "image/png"
    assert served.headers["x-content-type-options"] == "nosniff"


def test_image_extension_comes_from_real_content(auth_client: TestClient) -> None:
    files = {"image": ("photo.png", make_image("JPEG"), "image/png")}
    response = auth_client.post(
        f"{API}/posts", data=post_form(), files=files, headers=csrf_headers(auth_client)
    )
    assert response.status_code == 201
    assert response.json()["data"]["cover_image"].endswith(".jpg")


def test_duplicate_titles_get_unique_slugs(create_post: CreatePost) -> None:
    first = create_post()
    second = create_post()
    assert first["slug"] == "my-first-post"
    assert second["slug"].startswith("my-first-post-")
    assert first["slug"] != second["slug"]


def test_create_post_requires_authentication(client: TestClient) -> None:
    response = client.post(f"{API}/posts", data=post_form())
    assert response.status_code == 401


def test_create_post_field_validation(auth_client: TestClient) -> None:
    headers = csrf_headers(auth_client)
    response = auth_client.post(
        f"{API}/posts", data=post_form(title="ab", excerpt="short"), headers=headers
    )
    assert response.status_code == 422
    fields = {error["field"] for error in response.json()["data"]["errors"]}
    assert {"title", "excerpt"} <= fields

    missing = auth_client.post(f"{API}/posts", data={"title": "Only a title"}, headers=headers)
    assert missing.status_code == 422


def test_create_post_content_validation(auth_client: TestClient) -> None:
    headers = csrf_headers(auth_client)
    invalid_json = auth_client.post(
        f"{API}/posts", data=post_form(content="not json"), headers=headers
    )
    assert invalid_json.status_code == 422

    bad_type = auth_client.post(
        f"{API}/posts", data=post_form(content='[{"type":"script","text":"x"}]'), headers=headers
    )
    assert bad_type.status_code == 422

    no_paragraph = auth_client.post(
        f"{API}/posts",
        data=post_form(content='[{"type":"heading","text":"Only"}]'),
        headers=headers,
    )
    assert no_paragraph.status_code == 422
    assert "paragraph" in no_paragraph.json()["data"]["errors"][0]["message"]

    empty = auth_client.post(f"{API}/posts", data=post_form(content="[]"), headers=headers)
    assert empty.status_code == 422


# ---- images -----------------------------------------------------------------------------


def test_upload_fake_image_is_rejected(auth_client: TestClient, upload_dir) -> None:
    files = {"image": ("evil.png", b"<?php echo 'hacked'; ?>", "image/png")}
    response = auth_client.post(
        f"{API}/posts", data=post_form(), files=files, headers=csrf_headers(auth_client)
    )
    assert response.status_code == 400
    assert "format" in response.json()["message"].lower()
    assert _stored_files(upload_dir) == set()


def test_upload_corrupted_image_is_rejected(auth_client: TestClient) -> None:
    corrupted = make_image("PNG")[:40]
    files = {"image": ("broken.png", corrupted, "image/png")}
    response = auth_client.post(
        f"{API}/posts", data=post_form(), files=files, headers=csrf_headers(auth_client)
    )
    assert response.status_code == 400


def test_upload_unsupported_format_is_rejected(auth_client: TestClient) -> None:
    files = {"image": ("anim.gif", make_image("GIF"), "image/gif")}
    response = auth_client.post(
        f"{API}/posts", data=post_form(), files=files, headers=csrf_headers(auth_client)
    )
    assert response.status_code == 400


def test_upload_too_large_image_returns_413(auth_client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE", 1024)
    files = {"image": ("big.png", make_image("PNG", size=(800, 800)) + b"\0" * 2048, "image/png")}
    response = auth_client.post(
        f"{API}/posts", data=post_form(), files=files, headers=csrf_headers(auth_client)
    )
    assert response.status_code == 413
    assert response.json()["status"] == 413


def test_uploads_route_rejects_path_traversal(client: TestClient) -> None:
    assert client.get("/uploads/..%2F..%2Fetc%2Fpasswd").status_code == 404
    assert client.get("/uploads/notes.txt").status_code == 404


# ---- read -------------------------------------------------------------------------------


def test_list_posts_pagination(create_post: CreatePost, client: TestClient) -> None:
    for index in range(5):
        create_post(title=f"Post number {index}")
    response = client.get(f"{API}/posts", params={"page": 2, "size": 2})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 5
    assert data["pages"] == 3
    assert data["page"] == 2
    assert len(data["items"]) == 2


def test_list_posts_sorting(create_post: CreatePost, client: TestClient) -> None:
    for title in ("Oldest post", "Middle post", "Newest post"):
        create_post(title=title)
    newest = client.get(f"{API}/posts", params={"sort": "newest"}).json()["data"]["items"]
    oldest = client.get(f"{API}/posts", params={"sort": "oldest"}).json()["data"]["items"]
    assert newest[0]["title"] == "Newest post"
    assert oldest[0]["title"] == "Oldest post"


def test_list_posts_search_by_title(create_post: CreatePost, client: TestClient) -> None:
    create_post(title="Learning FastAPI")
    create_post(title="Cooking pasta")
    data = client.get(f"{API}/posts", params={"search": "fastapi"}).json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Learning FastAPI"
    assert client.get(f"{API}/posts", params={"search": "%"}).json()["data"]["total"] == 0


def test_list_posts_filter_by_author(
    create_post: CreatePost, other_client: TestClient, client: TestClient
) -> None:
    mine = create_post(title="Alice post")
    other_client.post(
        f"{API}/posts", data=post_form(title="Bob post"), headers=csrf_headers(other_client)
    )
    data = client.get(f"{API}/posts", params={"author_id": mine["author_id"]}).json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Alice post"


def test_get_post_detail(create_post: CreatePost, client: TestClient) -> None:
    post = create_post()
    response = client.get(f"{API}/posts/{post['id']}")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == post["id"]


def test_get_missing_post_returns_404(client: TestClient) -> None:
    response = client.get(f"{API}/posts/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json() == {"status": 404, "message": "Post not found", "data": None}


def test_get_post_invalid_id_returns_422(client: TestClient) -> None:
    assert client.get(f"{API}/posts/not-a-uuid").status_code == 422


# ---- update -----------------------------------------------------------------------------


def test_update_post(create_post: CreatePost, auth_client: TestClient) -> None:
    post = create_post()
    response = auth_client.put(
        f"{API}/posts/{post['id']}",
        data=post_form(title="Updated title", excerpt="An updated summary here."),
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["title"] == "Updated title"
    assert data["slug"] == "updated-title"
    assert data["excerpt"] == "An updated summary here."


def test_update_keeps_image_when_none_sent(
    create_post: CreatePost, auth_client: TestClient, upload_dir
) -> None:
    post = create_post(image=make_image())
    response = auth_client.put(
        f"{API}/posts/{post['id']}", data=post_form(), headers=csrf_headers(auth_client)
    )
    assert response.status_code == 200
    assert response.json()["data"]["cover_image"] == post["cover_image"]
    assert post["cover_image"] in _stored_files(upload_dir)


def test_update_replaces_image_and_deletes_old_file(
    create_post: CreatePost, auth_client: TestClient, upload_dir
) -> None:
    post = create_post(image=make_image("PNG"))
    files = {"image": ("new.webp", make_image("WEBP"), "image/webp")}
    response = auth_client.put(
        f"{API}/posts/{post['id']}",
        data=post_form(),
        files=files,
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 200
    new_key = response.json()["data"]["cover_image"]
    assert new_key.endswith(".webp")
    assert _stored_files(upload_dir) == {new_key}


def test_update_can_remove_image(
    create_post: CreatePost, auth_client: TestClient, upload_dir
) -> None:
    post = create_post(image=make_image())
    response = auth_client.put(
        f"{API}/posts/{post['id']}",
        data={**post_form(), "remove_image": "true"},
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 200
    assert response.json()["data"]["cover_image"] is None
    assert _stored_files(upload_dir) == set()


def test_cannot_update_post_of_another_user(
    create_post: CreatePost, other_client: TestClient
) -> None:
    post = create_post()
    response = other_client.put(
        f"{API}/posts/{post['id']}",
        data=post_form(title="Hijacked title"),
        headers=csrf_headers(other_client),
    )
    assert response.status_code == 403
    assert response.json()["message"] == "You can only modify your own posts"


def test_update_missing_post_returns_404(auth_client: TestClient) -> None:
    response = auth_client.put(
        f"{API}/posts/00000000-0000-0000-0000-000000000000",
        data=post_form(),
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 404


# ---- delete -----------------------------------------------------------------------------


def test_delete_post(create_post: CreatePost, auth_client: TestClient, upload_dir) -> None:
    post = create_post(image=make_image())
    response = auth_client.delete(f"{API}/posts/{post['id']}", headers=csrf_headers(auth_client))
    assert response.status_code == 204
    assert response.content == b""
    assert auth_client.get(f"{API}/posts/{post['id']}").status_code == 404
    assert _stored_files(upload_dir) == set()


def test_cannot_delete_post_of_another_user(
    create_post: CreatePost, other_client: TestClient, client: TestClient
) -> None:
    post = create_post()
    response = other_client.delete(f"{API}/posts/{post['id']}", headers=csrf_headers(other_client))
    assert response.status_code == 403
    assert client.get(f"{API}/posts/{post['id']}").status_code == 200


def test_delete_requires_authentication(create_post: CreatePost, client: TestClient) -> None:
    post = create_post()
    client.cookies.clear()
    assert client.delete(f"{API}/posts/{post['id']}").status_code == 401
