"use client";

import { useParams, useRouter } from "next/navigation";
import { toast } from "sonner";

import { PageHeader } from "@/components/layout/PageHeader";
import { PostForm } from "@/components/posts/PostForm";
import { Alert } from "@/components/ui/Alert";
import { ButtonLink } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageLoader } from "@/components/ui/Spinner";
import { useAuth } from "@/hooks/useAuth";
import { usePost } from "@/hooks/usePost";
import { postService } from "@/services/post.service";
import type { PostPayload } from "@/types/post";

export default function EditPostPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { user } = useAuth();
  const state = usePost(id);

  if (state.status === "loading") return <PageLoader label="Loading the post…" />;
  if (state.status === "not-found")
    return (
      <EmptyState
        title="Post not found"
        description={state.error}
        action={<ButtonLink href="/dashboard" variant="secondary">Back to dashboard</ButtonLink>}
      />
    );
  if (state.status === "error") return <Alert>{state.error}</Alert>;

  const { post } = state;
  if (post.author_id !== user?.id) {
    return (
      <EmptyState
        title="You cannot edit this post"
        description="Only the author of an article can modify it."
        action={<ButtonLink href="/dashboard" variant="secondary">Back to dashboard</ButtonLink>}
      />
    );
  }

  const handleSubmit = async (payload: PostPayload) => {
    const updated = await postService.update(post.id, payload);
    toast.success("Changes saved");
    router.push(`/posts/${updated.id}`);
  };

  return (
    <div className="space-y-8">
      <PageHeader title="Edit post" description={post.title} />
      <PostForm initialPost={post} submitLabel="Save changes" cancelHref="/dashboard" onSubmit={handleSubmit} />
    </div>
  );
}
