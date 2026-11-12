import Link from "next/link";

import type { Post } from "@/types/post";
import { formatDate } from "@/utils/format";

import { CoverImage } from "./CoverImage";

export function PostCard({ post }: { post: Post }) {
  return (
    <article className="group flex flex-col border border-line bg-surface">
      <Link href={`/posts/${post.id}`} className="block" tabIndex={-1} aria-hidden>
        <CoverImage src={post.cover_image_url} alt="" className="aspect-[16/9] w-full" />
      </Link>
      <div className="flex flex-1 flex-col p-5">
        <p className="text-xs text-muted">
          {post.author.name} · <time dateTime={post.created_at}>{formatDate(post.created_at)}</time>
        </p>
        <h2 className="mt-2 text-lg font-semibold leading-snug text-ink">
          <Link href={`/posts/${post.id}`} className="hover:text-accent">
            {post.title}
          </Link>
        </h2>
        <p className="mt-2 line-clamp-3 text-sm leading-relaxed text-body">{post.excerpt}</p>
        <Link href={`/posts/${post.id}`} className="mt-auto pt-4 text-sm font-medium text-accent hover:underline">
          Read article →
        </Link>
      </div>
    </article>
  );
}

export function PostCardSkeleton() {
  return (
    <div className="flex animate-pulse flex-col border border-line bg-surface" aria-hidden>
      <div className="aspect-[16/9] w-full bg-line/70" />
      <div className="space-y-3 p-5">
        <div className="h-3 w-1/3 bg-line" />
        <div className="h-5 w-4/5 bg-line" />
        <div className="h-3 w-full bg-line" />
        <div className="h-3 w-2/3 bg-line" />
      </div>
    </div>
  );
}
