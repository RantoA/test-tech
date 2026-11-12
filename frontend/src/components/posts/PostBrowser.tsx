"use client";

import { useState } from "react";

import { Alert } from "@/components/ui/Alert";
import { EmptyState } from "@/components/ui/EmptyState";
import { Input } from "@/components/ui/Field";
import { Pagination } from "@/components/ui/Pagination";
import { useDebounce } from "@/hooks/useDebounce";
import { usePosts } from "@/hooks/usePosts";
import type { SortOrder } from "@/types/post";

import { PostCard, PostCardSkeleton } from "./PostCard";

const PAGE_SIZE = 9;

/** Public post listing with title search, date sorting and pagination. */
export function PostBrowser() {
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<SortOrder>("newest");
  const [page, setPage] = useState(1);
  const search = useDebounce(query.trim());
  const { status, data, error, reload } = usePosts({ page, size: PAGE_SIZE, search, sort });

  const changePage = (next: number) => {
    setPage(next);
    window.scrollTo({ top: 0 });
  };

  return (
    <section aria-labelledby="articles-title" className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 id="articles-title" className="text-xl font-semibold text-ink">
            All articles
          </h2>
          <p className="mt-1 text-sm text-muted">
            {data ? `${data.total} article${data.total === 1 ? "" : "s"}` : " "}
          </p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row">
          <label htmlFor="search" className="sr-only">
            Search articles by title
          </label>
          <Input
            id="search"
            type="search"
            placeholder="Search by title…"
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              setPage(1);
            }}
            className="sm:w-72"
          />
          <label htmlFor="sort" className="sr-only">
            Sort articles
          </label>
          <select
            id="sort"
            value={sort}
            onChange={(event) => {
              setSort(event.target.value as SortOrder);
              setPage(1);
            }}
            className="h-10 border border-line-strong bg-surface px-3 text-sm text-ink focus:border-accent focus:outline-none"
          >
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
          </select>
        </div>
      </div>

      {status === "error" && (
        <Alert>
          {error}{" "}
          <button type="button" className="font-medium underline" onClick={reload}>
            Retry
          </button>
        </Alert>
      )}

      {status === "loading" && !data ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }, (_, index) => (
            <PostCardSkeleton key={index} />
          ))}
        </div>
      ) : data && data.items.length === 0 ? (
        <EmptyState
          title={search ? "No article matches your search" : "No article published yet"}
          description={search ? `Nothing found for “${search}”. Try another title.` : "Be the first to publish an article."}
        />
      ) : data ? (
        <div className={status === "loading" ? "opacity-60 transition-opacity" : undefined}>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {data.items.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>
          <div className="mt-8">
            <Pagination page={data.page} pages={data.pages} onChange={changePage} />
          </div>
        </div>
      ) : null}
    </section>
  );
}
