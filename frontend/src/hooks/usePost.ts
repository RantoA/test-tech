"use client";

import { useEffect, useState } from "react";

import { ApiError, getErrorMessage } from "@/services/api";
import { postService } from "@/services/post.service";
import type { Post } from "@/types/post";

type State =
  | { status: "loading"; post: null; error: null }
  | { status: "success"; post: Post; error: null }
  | { status: "not-found"; post: null; error: string }
  | { status: "error"; post: null; error: string };

type Settled = Exclude<State, { status: "loading" }> & { id: string };

export function usePost(id: string | undefined): State {
  const [settled, setSettled] = useState<Settled | null>(null);

  useEffect(() => {
    if (!id) return;
    const controller = new AbortController();
    postService
      .get(id, controller.signal)
      .then((post) => setSettled({ id, status: "success", post, error: null }))
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;
        const notFound = error instanceof ApiError && (error.status === 404 || error.status === 422);
        setSettled(
          notFound
            ? { id, status: "not-found", post: null, error: "This post does not exist or has been deleted." }
            : { id, status: "error", post: null, error: getErrorMessage(error) },
        );
      });
    return () => controller.abort();
  }, [id]);

  if (!settled || settled.id !== id) return { status: "loading", post: null, error: null };
  return settled;
}
