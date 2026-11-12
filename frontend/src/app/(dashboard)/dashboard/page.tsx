"use client";

import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/layout/PageHeader";
import { CoverImage } from "@/components/posts/CoverImage";
import { Alert } from "@/components/ui/Alert";
import { Button, ButtonLink } from "@/components/ui/Button";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { EmptyState } from "@/components/ui/EmptyState";
import { Pagination } from "@/components/ui/Pagination";
import { PageLoader } from "@/components/ui/Spinner";
import { useAuth } from "@/hooks/useAuth";
import { usePosts } from "@/hooks/usePosts";
import { getErrorMessage } from "@/services/api";
import { postService } from "@/services/post.service";
import type { Post } from "@/types/post";
import { formatDate } from "@/utils/format";

const PAGE_SIZE = 10;

export default function DashboardPage() {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [toDelete, setToDelete] = useState<Post | null>(null);
  const [deleting, setDeleting] = useState(false);
  const { status, data, error, reload } = usePosts(
    { page, size: PAGE_SIZE, author_id: user?.id, sort: "newest" },
    !!user,
  );

  const confirmDelete = async () => {
    if (!toDelete) return;
    setDeleting(true);
    try {
      await postService.remove(toDelete.id);
      toast.success("Post deleted");
      setToDelete(null);
      if (data && data.items.length === 1 && page > 1) setPage(page - 1);
      else reload();
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setDeleting(false);
    }
  };

  const total = data?.total ?? 0;

  return (
    <div className="space-y-8">
      <PageHeader
        title="Dashboard"
        description={`Welcome, ${user?.name}. Manage your articles from here.`}
        actions={<ButtonLink href="/posts/new">New post</ButtonLink>}
      />

      <dl className="grid grid-cols-1 border border-line bg-surface sm:grid-cols-3">
        <div className="border-b border-line p-5 sm:border-b-0 sm:border-r">
          <dt className="text-xs font-medium uppercase tracking-wider text-muted">Total articles</dt>
          <dd className="mt-2 text-3xl font-semibold text-ink">{status === "loading" && !data ? "—" : total}</dd>
        </div>
        <div className="border-b border-line p-5 sm:border-b-0 sm:border-r">
          <dt className="text-xs font-medium uppercase tracking-wider text-muted">Latest publication</dt>
          <dd className="mt-2 text-base font-medium text-ink">
            {data?.items[0] && page === 1 ? formatDate(data.items[0].created_at) : "—"}
          </dd>
        </div>
        <div className="p-5">
          <dt className="text-xs font-medium uppercase tracking-wider text-muted">Account</dt>
          <dd className="mt-2 truncate text-base font-medium text-ink">{user?.email}</dd>
        </div>
      </dl>

      {status === "error" && (
        <Alert>
          {error}{" "}
          <button type="button" className="font-medium underline" onClick={reload}>
            Retry
          </button>
        </Alert>
      )}

      {status === "loading" && !data ? (
        <PageLoader label="Loading your articles…" />
      ) : data && data.items.length === 0 ? (
        <EmptyState
          title="You have not written any article yet"
          description="Create your first post: add a title, a summary, structured content and a cover image."
          action={<ButtonLink href="/posts/new">Write your first post</ButtonLink>}
        />
      ) : data ? (
        <div className="space-y-6">
          <div className="overflow-x-auto border border-line bg-surface">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead className="border-b border-line bg-canvas text-xs uppercase tracking-wider text-muted">
                <tr>
                  <th scope="col" className="px-4 py-3 font-medium">Article</th>
                  <th scope="col" className="px-4 py-3 font-medium">Created</th>
                  <th scope="col" className="px-4 py-3 font-medium">Updated</th>
                  <th scope="col" className="px-4 py-3 text-right font-medium">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {data.items.map((post) => (
                  <tr key={post.id} className="align-middle">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-4">
                        <CoverImage src={post.cover_image_url} alt="" className="h-12 w-20 shrink-0 text-[10px]" />
                        <div className="min-w-0">
                          <Link href={`/posts/${post.id}`} className="font-medium text-ink hover:text-accent">
                            {post.title}
                          </Link>
                          <p className="truncate text-xs text-muted">{post.excerpt}</p>
                        </div>
                      </div>
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-muted">{formatDate(post.created_at)}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-muted">{formatDate(post.updated_at)}</td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-2">
                        <ButtonLink href={`/posts/${post.id}/edit`} variant="secondary" size="sm">
                          Edit
                        </ButtonLink>
                        <Button
                          variant="secondary"
                          size="sm"
                          className="text-danger"
                          onClick={() => setToDelete(post)}
                        >
                          Delete
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination page={data.page} pages={data.pages} onChange={setPage} />
        </div>
      ) : null}

      <ConfirmDialog
        open={toDelete !== null}
        title="Delete this post?"
        description={`"${toDelete?.title ?? ""}" will be permanently deleted, including its cover image. This action cannot be undone.`}
        confirmLabel="Delete post"
        loading={deleting}
        onConfirm={confirmDelete}
        onCancel={() => setToDelete(null)}
      />
    </div>
  );
}
