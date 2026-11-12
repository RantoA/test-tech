import { format } from "date-fns";

import type { Post } from "@/types/post";

/** Display name of a post author; editorial posts are signed by the platform. */
export function authorName(post: Pick<Post, "author">): string {
  return post.author?.name ?? "my-blog";
}

export function formatDate(value: string): string {
  return format(new Date(value), "MMM d, yyyy");
}

export function formatDateTime(value: string): string {
  return format(new Date(value), "MMM d, yyyy 'at' HH:mm");
}

export function readingTime(texts: string[]): number {
  const words = texts.join(" ").trim().split(/\s+/).filter(Boolean).length;
  return Math.max(1, Math.round(words / 220));
}
