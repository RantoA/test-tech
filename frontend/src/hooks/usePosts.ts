"use client";

import { useCallback, useEffect, useState } from "react";

import { getErrorMessage } from "@/services/api";
import { postService } from "@/services/post.service";
import type { Paginated } from "@/types/api";
import type { Post, PostListParams } from "@/types/post";

interface Result {
  key: string;
  data: Paginated<Post> | null;
  error: string | null;
}

/**
 * Fetch a paginated list of posts; re-fetches whenever the params change.
 * The previous page stays available while the next one loads (no layout flash).
 */
export function usePosts(params: PostListParams, enabled = true) {
  const [reloadKey, setReloadKey] = useState(0);
  const [result, setResult] = useState<Result | null>(null);
  const [lastData, setLastData] = useState<Paginated<Post> | null>(null);
  const { page, size, search, author_id, sort } = params;
  const key = JSON.stringify([page, size, search, author_id, sort, reloadKey]);

  useEffect(() => {
    if (!enabled) return;
    const controller = new AbortController();
    postService
      .list({ page, size, search, author_id, sort }, controller.signal)
      .then((data) => {
        setResult({ key, data, error: null });
        setLastData(data);
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) setResult({ key, data: null, error: getErrorMessage(error) });
      });
    return () => controller.abort();
  }, [key, page, size, search, author_id, sort, enabled]);

  const reload = useCallback(() => setReloadKey((value) => value + 1), []);
  const settled = result?.key === key ? result : null;

  if (!settled) return { status: "loading" as const, data: lastData, error: null, reload };
  if (settled.error) return { status: "error" as const, data: lastData, error: settled.error, reload };
  return { status: "success" as const, data: settled.data ?? lastData, error: null, reload };
}
