"use client";

import { ButtonLink } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";

import { Container } from "./Container";

export function Hero() {
  const { user, loading } = useAuth();
  return (
    <section className="border-b border-line bg-surface">
      <Container className="py-14 sm:py-20">
        <p className="text-xs font-semibold uppercase tracking-widest text-accent">Blog Post Manager</p>
        <h1 className="mt-3 max-w-2xl text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
          Write, publish and manage your articles in one place.
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-relaxed text-muted">
          my-blog is a simple publishing platform: structure your content with titles, subtitles and
          paragraphs, add a cover image, and keep full control over your own posts.
        </p>
        <div className="mt-8 flex min-h-10 flex-wrap gap-3">
          {loading ? null : user ? (
            <>
              <ButtonLink href="/posts/new">Write a post</ButtonLink>
              <ButtonLink href="/dashboard" variant="secondary">
                Go to dashboard
              </ButtonLink>
            </>
          ) : (
            <>
              <ButtonLink href="/register">Get started</ButtonLink>
              <ButtonLink href="/login" variant="secondary">
                Log in
              </ButtonLink>
            </>
          )}
        </div>
      </Container>
    </section>
  );
}
