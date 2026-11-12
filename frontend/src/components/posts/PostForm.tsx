"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm, useWatch } from "react-hook-form";

import { Alert } from "@/components/ui/Alert";
import { Button, ButtonLink } from "@/components/ui/Button";
import { FormField, Input, Textarea } from "@/components/ui/Field";
import { postSchema, type PostFormValues } from "@/schemas/post.schema";
import { getErrorMessage } from "@/services/api";
import type { Post, PostPayload } from "@/types/post";
import { applyApiFieldErrors } from "@/utils/form-errors";

import { BlockEditor } from "./BlockEditor";
import { ImageUpload, type ImageSelection } from "./ImageUpload";

interface PostFormProps {
  initialPost?: Post;
  submitLabel: string;
  cancelHref: string;
  onSubmit: (payload: PostPayload) => Promise<void>;
}

const EMPTY_BLOCKS: PostFormValues["blocks"] = [
  { type: "heading", text: "" },
  { type: "paragraph", text: "" },
];

export function PostForm({ initialPost, submitLabel, cancelHref, onSubmit }: PostFormProps) {
  const [image, setImage] = useState<ImageSelection>({ file: null, removeExisting: false });
  const [formError, setFormError] = useState<string | null>(null);

  const {
    control,
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<PostFormValues>({
    resolver: zodResolver(postSchema),
    defaultValues: {
      title: initialPost?.title ?? "",
      excerpt: initialPost?.excerpt ?? "",
      blocks: initialPost?.content.map(({ type, text }) => ({ type, text })) ?? EMPTY_BLOCKS,
    },
  });

  const excerptLength = useWatch({ control, name: "excerpt" })?.length ?? 0;

  const submit = handleSubmit(async (values) => {
    setFormError(null);
    try {
      await onSubmit({
        title: values.title,
        excerpt: values.excerpt,
        content: values.blocks,
        image: image.file,
        removeImage: image.removeExisting,
      });
    } catch (error) {
      if (!applyApiFieldErrors(error, setError, { content: "blocks" })) {
        setFormError(getErrorMessage(error));
      }
    }
  });

  return (
    <form onSubmit={submit} noValidate className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px]">
      <div className="space-y-6">
        {formError && <Alert>{formError}</Alert>}

        <FormField id="title" label="Title" error={errors.title?.message}>
          <Input
            id="title"
            placeholder="A clear, descriptive title"
            className="text-base"
            maxLength={200}
            invalid={!!errors.title}
            disabled={isSubmitting}
            {...register("title")}
          />
        </FormField>

        <FormField
          id="excerpt"
          label="Summary"
          error={errors.excerpt?.message}
          hint={`${excerptLength}/500 — shown in article lists and at the top of the article.`}
        >
          <Textarea
            id="excerpt"
            rows={3}
            maxLength={500}
            placeholder="Summarize your article in one or two sentences"
            invalid={!!errors.excerpt}
            disabled={isSubmitting}
            {...register("excerpt")}
          />
        </FormField>

        <BlockEditor control={control} register={register} errors={errors} disabled={isSubmitting} />
      </div>

      <aside className="space-y-6 lg:sticky lg:top-24 lg:self-start">
        <ImageUpload
          existingUrl={initialPost?.cover_image_url}
          value={image}
          onChange={setImage}
          disabled={isSubmitting}
        />
        <div className="flex flex-col gap-2 border-t border-line pt-6">
          <Button type="submit" loading={isSubmitting}>
            {submitLabel}
          </Button>
          <ButtonLink href={cancelHref} variant="secondary">
            Cancel
          </ButtonLink>
        </div>
      </aside>
    </form>
  );
}
