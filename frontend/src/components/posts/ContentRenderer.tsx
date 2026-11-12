import type { ContentBlock } from "@/types/post";

/** Renders structured blocks as plain React text nodes (no HTML injection possible). */
export function ContentRenderer({ blocks }: { blocks: ContentBlock[] }) {
  return (
    <div className="space-y-5">
      {blocks.map((block, index) => {
        switch (block.type) {
          case "heading":
            return (
              <h2 key={index} className="pt-4 text-2xl font-semibold tracking-tight text-ink">
                {block.text}
              </h2>
            );
          case "subheading":
            return (
              <h3 key={index} className="pt-2 text-lg font-semibold text-ink">
                {block.text}
              </h3>
            );
          default:
            return (
              <p key={index} className="whitespace-pre-line text-base leading-8 text-body">
                {block.text}
              </p>
            );
        }
      })}
    </div>
  );
}
