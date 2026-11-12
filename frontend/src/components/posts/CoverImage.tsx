/* eslint-disable @next/next/no-img-element -- images are served by the API on another origin */
import { cn } from "@/utils/cn";

export function CoverImage({
  src,
  alt,
  className,
  priority = false,
}: {
  src: string | null;
  alt: string;
  className?: string;
  priority?: boolean;
}) {
  if (!src) {
    return (
      <div
        aria-hidden
        className={cn("flex items-center justify-center bg-line/60 text-xs uppercase tracking-widest text-muted", className)}
      >
        No image
      </div>
    );
  }
  return (
    <img
      src={src}
      alt={alt}
      loading={priority ? "eager" : "lazy"}
      decoding="async"
      className={cn("object-cover", className)}
    />
  );
}
