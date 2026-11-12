"use client";

import { useFieldArray, type Control, type FieldErrors, type UseFormRegister } from "react-hook-form";

import { Button } from "@/components/ui/Button";
import { FieldError, Input, Textarea } from "@/components/ui/Field";
import { BLOCK_LIMITS, type PostFormValues } from "@/schemas/post.schema";
import type { BlockType } from "@/types/post";

const BLOCK_LABELS: Record<BlockType, string> = {
  heading: "Title",
  subheading: "Subtitle",
  paragraph: "Paragraph",
};

const BLOCK_PLACEHOLDERS: Record<BlockType, string> = {
  heading: "Section title",
  subheading: "Section subtitle",
  paragraph: "Write your paragraph…",
};

interface BlockEditorProps {
  control: Control<PostFormValues>;
  register: UseFormRegister<PostFormValues>;
  errors: FieldErrors<PostFormValues>;
  disabled?: boolean;
}

/** Structured content editor: an ordered list of title / subtitle / paragraph blocks. */
export function BlockEditor({ control, register, errors, disabled }: BlockEditorProps) {
  const { fields, append, remove, move } = useFieldArray({ control, name: "blocks" });
  const rootError = errors.blocks?.root?.message ?? errors.blocks?.message;

  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between">
        <span className="text-sm font-medium text-ink">Content</span>
        <span className="text-xs text-muted">
          {fields.length} block{fields.length === 1 ? "" : "s"}
        </span>
      </div>

      <ol className="space-y-3">
        {fields.map((field, index) => {
          const type = field.type as BlockType;
          const error = errors.blocks?.[index]?.text?.message;
          const inputId = `block-${field.id}`;
          return (
            <li key={field.id} className="border border-line bg-surface">
              <div className="flex items-center justify-between border-b border-line bg-canvas px-3 py-1.5">
                <label htmlFor={inputId} className="text-xs font-semibold uppercase tracking-wider text-muted">
                  {index + 1}. {BLOCK_LABELS[type]}
                </label>
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 px-2"
                    disabled={disabled || index === 0}
                    onClick={() => move(index, index - 1)}
                    aria-label={`Move block ${index + 1} up`}
                  >
                    ↑
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 px-2"
                    disabled={disabled || index === fields.length - 1}
                    onClick={() => move(index, index + 1)}
                    aria-label={`Move block ${index + 1} down`}
                  >
                    ↓
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 px-2 text-danger hover:text-danger"
                    disabled={disabled || fields.length === 1}
                    onClick={() => remove(index)}
                    aria-label={`Remove block ${index + 1}`}
                  >
                    Remove
                  </Button>
                </div>
              </div>
              <div className="p-3">
                <input type="hidden" {...register(`blocks.${index}.type` as const)} />
                {type === "paragraph" ? (
                  <Textarea
                    id={inputId}
                    rows={5}
                    maxLength={BLOCK_LIMITS.paragraph}
                    placeholder={BLOCK_PLACEHOLDERS[type]}
                    invalid={!!error}
                    disabled={disabled}
                    {...register(`blocks.${index}.text` as const)}
                  />
                ) : (
                  <Input
                    id={inputId}
                    maxLength={BLOCK_LIMITS[type]}
                    placeholder={BLOCK_PLACEHOLDERS[type]}
                    invalid={!!error}
                    disabled={disabled}
                    className={type === "heading" ? "text-base font-semibold" : "font-medium"}
                    {...register(`blocks.${index}.text` as const)}
                  />
                )}
                <FieldError message={error} />
              </div>
            </li>
          );
        })}
      </ol>

      <FieldError message={rootError} />

      <div className="mt-3 flex flex-wrap gap-2">
        {(Object.keys(BLOCK_LABELS) as BlockType[]).map((type) => (
          <Button
            key={type}
            variant="secondary"
            size="sm"
            disabled={disabled}
            onClick={() => append({ type, text: "" })}
          >
            + {BLOCK_LABELS[type]}
          </Button>
        ))}
      </div>
    </div>
  );
}
