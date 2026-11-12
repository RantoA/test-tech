import type { Author } from "./user";

export type BlockType = "heading" | "subheading" | "paragraph";

export interface ContentBlock {
  type: BlockType;
  text: string;
}

export interface Post {
  id: string;
  title: string;
  slug: string;
  excerpt: string;
  content: ContentBlock[];
  cover_image: string | null;
  cover_image_url: string | null;
  /** null for editorial posts published by the platform itself. */
  author_id: string | null;
  author: Author | null;
  created_at: string;
  updated_at: string;
}

export type SortOrder = "newest" | "oldest";

export interface PostListParams {
  page?: number;
  size?: number;
  search?: string;
  author_id?: string;
  sort?: SortOrder;
}

export interface PostPayload {
  title: string;
  excerpt: string;
  content: ContentBlock[];
  image?: File | null;
  removeImage?: boolean;
}
