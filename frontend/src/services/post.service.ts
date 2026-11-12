import type { Paginated } from "@/types/api";
import type { Post, PostListParams, PostPayload } from "@/types/post";

import { api } from "./api";

function toFormData(payload: PostPayload): FormData {
  const form = new FormData();
  form.append("title", payload.title);
  form.append("excerpt", payload.excerpt);
  form.append("content", JSON.stringify(payload.content));
  if (payload.image) form.append("image", payload.image);
  if (payload.removeImage) form.append("remove_image", "true");
  return form;
}

export const postService = {
  list: (params: PostListParams = {}, signal?: AbortSignal) =>
    api.get<Paginated<Post>>("/posts", { query: { ...params }, signal }),
  get: (id: string, signal?: AbortSignal) => api.get<Post>(`/posts/${id}`, { signal }),
  create: (payload: PostPayload) => api.post<Post>("/posts", toFormData(payload)),
  update: (id: string, payload: PostPayload) => api.put<Post>(`/posts/${id}`, toFormData(payload)),
  remove: (id: string) => api.delete<void>(`/posts/${id}`),
};
