"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import { Container } from "@/components/layout/Container";
import { Alert } from "@/components/ui/Alert";
import { ButtonLink } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageLoader } from "@/components/ui/Spinner";
import { useAuth } from "@/hooks/useAuth";
import { usePost } from "@/hooks/usePost";
import { authorName, formatDate, formatDateTime, readingTime } from "@/utils/format";

import { ContentRenderer } from "./ContentRenderer";
import { CoverImage } from "./CoverImage";

export function PostDetail() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const state = usePost(id);

  if (state.status === "loading") return <PageLoader label="Loading the article…" />;
  if (state.status !== "success") {
    return (
      <Container className="py-16">
        {state.status === "not-found" ? (
          <EmptyState
            title="Article not found"
            description={state.error}
            action={<ButtonLink href="/" variant="secondary">Back to articles</ButtonLink>}
          />
        ) : (
          <Alert>{state.error}</Alert>
        )}
      </Container>
    );
  }

  const { post } = state;
  const isAuthor = !!user && user.id === post.author_id;
  const minutes = readingTime(post.content.map((block) => block.text));
  const edited = post.updated_at !== post.created_at;

  return (
    <article className="bg-surface">
      <Container className="max-w-3xl py-12">
        <nav className="flex items-center justify-between text-sm">
          <Link href="/" className="text-muted hover:text-ink">
            ← All articles
          </Link>
          {isAuthor && (
            <ButtonLink href={`/posts/${post.id}/edit`} variant="secondary" size="sm">
              Edit post
            </ButtonLink>
          )}
        </nav>

        <header className="mt-8">
          <h1 className="text-3xl font-semibold leading-tight tracking-tight text-ink sm:text-4xl">{post.title}</h1>
          <p className="mt-4 text-lg leading-relaxed text-muted">{post.excerpt}</p>
          <div className="mt-6 flex flex-wrap items-center gap-x-3 gap-y-1 border-y border-line py-4 text-sm text-muted">
            <span className="font-medium text-ink">{authorName(post)}</span>
            <span aria-hidden>·</span>
            <time dateTime={post.created_at}>Published {formatDate(post.created_at)}</time>
            <span aria-hidden>·</span>
            <span>{minutes} min read</span>
            {edited && (
              <>
                <span aria-hidden>·</span>
                <span title={formatDateTime(post.updated_at)}>Updated {formatDate(post.updated_at)}</span>
              </>
            )}
          </div>
        </header>
      </Container>

      {post.cover_image_url && (
        <Container className="max-w-4xl">
          <CoverImage src={post.cover_image_url} alt={post.title} priority className="aspect-[16/9] w-full" />
        </Container>
      )}

      <Container className="max-w-3xl py-12">
        <ContentRenderer blocks={post.content} />
      </Container>
    </article>
  );
}
