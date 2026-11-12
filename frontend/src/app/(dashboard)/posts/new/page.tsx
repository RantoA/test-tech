"use client";

import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { PageHeader } from "@/components/layout/PageHeader";
import { PostForm } from "@/components/posts/PostForm";
import { postService } from "@/services/post.service";
import type { PostPayload } from "@/types/post";

export default function NewPostPage() {
  const router = useRouter();

  const handleSubmit = async (payload: PostPayload) => {
    const post = await postService.create(payload);
    toast.success("Post published");
    router.push(`/posts/${post.id}`);
  };

  return (
    <div className="space-y-8">
      <PageHeader title="New post" description="Write your article using titles, subtitles and paragraphs." />
      <PostForm submitLabel="Publish" cancelHref="/dashboard" onSubmit={handleSubmit} />
    </div>
  );
}
