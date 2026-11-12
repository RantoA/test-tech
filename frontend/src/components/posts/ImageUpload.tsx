"use client";

/* eslint-disable @next/next/no-img-element -- local blob previews and API-hosted images */
import { useEffect, useId, useMemo, useRef, useState } from "react";

import { Button } from "@/components/ui/Button";
import { FieldError, FieldHint } from "@/components/ui/Field";
import { ACCEPTED_IMAGE_TYPES, validateImage } from "@/schemas/post.schema";

export interface ImageSelection {
  file: File | null;
  removeExisting: boolean;
}

interface ImageUploadProps {
  existingUrl?: string | null;
  value: ImageSelection;
  onChange: (value: ImageSelection) => void;
  disabled?: boolean;
}

/** Cover image picker with preview. Supports keep / replace / remove of an existing image. */
export function ImageUpload({ existingUrl, value, onChange, disabled }: ImageUploadProps) {
  const inputId = useId();
  const inputRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | undefined>();
  const previewUrl = useMemo(() => (value.file ? URL.createObjectURL(value.file) : null), [value.file]);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const shownUrl = previewUrl ?? (value.removeExisting ? null : (existingUrl ?? null));
  const isExisting = !previewUrl && !!shownUrl;

  const handleFile = (file: File | undefined) => {
    if (!file) return;
    const message = validateImage(file);
    if (message) {
      setError(message);
      if (inputRef.current) inputRef.current.value = "";
      return;
    }
    setError(undefined);
    onChange({ file, removeExisting: false });
  };

  const clearSelection = () => {
    if (inputRef.current) inputRef.current.value = "";
    setError(undefined);
    onChange({ file: null, removeExisting: false });
  };

  return (
    <div>
      <span className="mb-1.5 block text-sm font-medium text-ink">Cover image</span>
      <div className="border border-line bg-surface">
        {shownUrl ? (
          <img src={shownUrl} alt="Cover preview" className="aspect-[16/9] w-full object-cover" />
        ) : (
          <label
            htmlFor={inputId}
            className="flex aspect-[16/9] w-full cursor-pointer flex-col items-center justify-center gap-1 bg-canvas text-sm text-muted hover:bg-line/40"
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              event.preventDefault();
              if (!disabled) handleFile(event.dataTransfer.files?.[0]);
            }}
          >
            <span className="font-medium text-ink">Click to upload or drag an image here</span>
            <span className="text-xs">JPEG, PNG or WebP — 5 MB max</span>
          </label>
        )}
        <div className="flex flex-wrap items-center gap-2 border-t border-line px-3 py-2">
          <Button
            variant="secondary"
            size="sm"
            disabled={disabled}
            onClick={() => inputRef.current?.click()}
          >
            {shownUrl ? "Replace image" : "Choose image"}
          </Button>
          {previewUrl && (
            <Button variant="ghost" size="sm" disabled={disabled} onClick={clearSelection}>
              {existingUrl && !value.removeExisting ? "Keep current image" : "Cancel"}
            </Button>
          )}
          {isExisting && (
            <Button
              variant="ghost"
              size="sm"
              className="text-danger hover:text-danger"
              disabled={disabled}
              onClick={() => onChange({ file: null, removeExisting: true })}
            >
              Remove image
            </Button>
          )}
          {value.removeExisting && !previewUrl && existingUrl && (
            <Button variant="ghost" size="sm" disabled={disabled} onClick={clearSelection}>
              Undo remove
            </Button>
          )}
          <span className="ml-auto truncate text-xs text-muted">
            {value.file ? value.file.name : isExisting ? "Current image" : "No image"}
          </span>
        </div>
      </div>
      <input
        ref={inputRef}
        id={inputId}
        type="file"
        accept={ACCEPTED_IMAGE_TYPES.join(",")}
        className="sr-only"
        disabled={disabled}
        onChange={(event) => handleFile(event.target.files?.[0])}
      />
      {error ? <FieldError message={error} /> : <FieldHint>Optional. A 16:9 image works best.</FieldHint>}
    </div>
  );
}
