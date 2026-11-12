import { z } from "zod";

export const MAX_IMAGE_SIZE = 5 * 1024 * 1024;
export const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];

export const BLOCK_LIMITS = { heading: 200, subheading: 200, paragraph: 10_000 } as const;

const blockSchema = z
  .object({
    type: z.enum(["heading", "subheading", "paragraph"]),
    text: z.string().trim().min(1, "This block cannot be empty"),
  })
  .superRefine((block, ctx) => {
    const limit = BLOCK_LIMITS[block.type];
    if (block.text.length > limit) {
      ctx.addIssue({
        code: "custom",
        path: ["text"],
        message: `Must be at most ${limit.toLocaleString()} characters`,
      });
    }
  });

export const postSchema = z.object({
  title: z
    .string()
    .trim()
    .min(3, "Title must be at least 3 characters")
    .max(200, "Title must be at most 200 characters"),
  excerpt: z
    .string()
    .trim()
    .min(10, "Summary must be at least 10 characters")
    .max(500, "Summary must be at most 500 characters"),
  blocks: z
    .array(blockSchema)
    .min(1, "Add at least one block")
    .max(200, "A post can contain at most 200 blocks")
    .refine((blocks) => blocks.some((block) => block.type === "paragraph"), {
      message: "Content must contain at least one paragraph",
    }),
});

export type PostFormValues = z.infer<typeof postSchema>;

export function validateImage(file: File): string | null {
  if (!ACCEPTED_IMAGE_TYPES.includes(file.type)) return "Only JPEG, PNG and WebP images are allowed";
  if (file.size > MAX_IMAGE_SIZE) return "Image must be 5 MB or smaller";
  return null;
}
