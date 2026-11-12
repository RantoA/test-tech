"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Container } from "@/components/layout/Container";
import { ButtonLink } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";
import { usePosts } from "@/hooks/usePosts";
import { cn } from "@/utils/cn";
import { authorName, formatDate } from "@/utils/format";

import { CoverImage } from "./CoverImage";

const SLIDE_COUNT = 4;
const INTERVAL_MS = 6000;

function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReduced(query.matches);
    update();
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);
  return reduced;
}

/** Auto-scrolling banner showing the latest published posts. */
export function LatestPostsBanner() {
  const { user } = useAuth();
  const { status, data } = usePosts({ page: 1, size: SLIDE_COUNT, sort: "newest" });
  const posts = data?.items ?? [];
  const count = posts.length;

  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(false);
  const reducedMotion = usePrefersReducedMotion();
  const active = count > 0 ? index % count : 0;

  const goTo = useCallback((next: number) => setIndex(((next % count) + count) % count), [count]);

  useEffect(() => {
    if (count <= 1 || paused || reducedMotion) return;
    const timer = setInterval(() => setIndex((current) => (current + 1) % count), INTERVAL_MS);
    return () => clearInterval(timer);
  }, [count, paused, reducedMotion]);

  if (status === "loading" && !data) {
    return (
      <section className="border-b border-line bg-surface" aria-hidden>
        <Container className="grid animate-pulse gap-8 py-10 md:grid-cols-2 md:py-12">
          <div className="aspect-[16/9] w-full bg-line/70" />
          <div className="space-y-4 self-center">
            <div className="h-3 w-1/4 bg-line" />
            <div className="h-8 w-4/5 bg-line" />
            <div className="h-4 w-full bg-line" />
            <div className="h-4 w-2/3 bg-line" />
          </div>
        </Container>
      </section>
    );
  }

  if (count === 0) {
    return (
      <section className="border-b border-line bg-surface">
        <Container className="flex flex-col items-start gap-4 py-12">
          <p className="text-xs font-semibold uppercase tracking-widest text-accent">Latest articles</p>
          <h1 className="text-2xl font-semibold tracking-tight text-ink">No article has been published yet.</h1>
          <ButtonLink href={user ? "/posts/new" : "/register"}>
            {user ? "Write the first post" : "Create an account to publish"}
          </ButtonLink>
        </Container>
      </section>
    );
  }

  return (
    <section
      className="border-b border-line bg-surface"
      aria-roledescription="carousel"
      aria-label="Latest articles"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onFocus={() => setPaused(true)}
      onBlur={() => setPaused(false)}
    >
      <Container className="py-10 md:py-12">
        <div className="overflow-hidden">
          <div
            className={cn("flex", !reducedMotion && "transition-transform duration-500 ease-out")}
            style={{ transform: `translateX(-${active * 100}%)` }}
          >
            {posts.map((post, slide) => (
              <article
                key={post.id}
                className="grid w-full shrink-0 gap-6 md:grid-cols-2 md:gap-10"
                aria-roledescription="slide"
                aria-label={`${slide + 1} of ${count}`}
                aria-hidden={slide !== active}
                inert={slide !== active}
              >
                <Link href={`/posts/${post.id}`} tabIndex={-1} className="block">
                  <CoverImage
                    src={post.cover_image_url}
                    alt={post.title}
                    priority={slide === 0}
                    className="aspect-[16/9] w-full"
                  />
                </Link>
                <div className="flex flex-col justify-center">
                  <p className="text-xs font-semibold uppercase tracking-widest text-accent">
                    Latest articles
                  </p>
                  <h1 className="mt-3 text-2xl font-semibold leading-tight tracking-tight text-ink sm:text-3xl">
                    <Link href={`/posts/${post.id}`} className="hover:text-accent">
                      {post.title}
                    </Link>
                  </h1>
                  <p className="mt-3 line-clamp-3 text-base leading-relaxed text-muted">{post.excerpt}</p>
                  <p className="mt-4 text-sm text-muted">
                    <span className="font-medium text-ink">{authorName(post)}</span> ·{" "}
                    <time dateTime={post.created_at}>{formatDate(post.created_at)}</time>
                  </p>
                  <Link
                    href={`/posts/${post.id}`}
                    className="mt-6 text-sm font-medium text-accent hover:underline"
                  >
                    Read article →
                  </Link>
                </div>
              </article>
            ))}
          </div>
        </div>

        {count > 1 && (
          <div className="mt-8 flex items-center justify-between gap-4 border-t border-line pt-4">
            <div className="flex gap-2" role="group" aria-label="Choose a slide">
              {posts.map((post, slide) => (
                <button
                  key={post.id}
                  type="button"
                  onClick={() => goTo(slide)}
                  aria-label={`Show article ${slide + 1}: ${post.title}`}
                  aria-current={slide === active}
                  className={cn(
                    "h-1 w-8 transition-colors sm:w-12",
                    slide === active ? "bg-accent" : "bg-line-strong hover:bg-muted",
                  )}
                />
              ))}
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => goTo(active - 1)}
                aria-label="Previous article"
                className="inline-flex h-8 w-8 items-center justify-center border border-line-strong text-ink hover:bg-canvas"
              >
                ←
              </button>
              <button
                type="button"
                onClick={() => goTo(active + 1)}
                aria-label="Next article"
                className="inline-flex h-8 w-8 items-center justify-center border border-line-strong text-ink hover:bg-canvas"
              >
                →
              </button>
            </div>
          </div>
        )}
      </Container>
    </section>
  );
}
