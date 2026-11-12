import type { FieldValues, Path, UseFormSetError } from "react-hook-form";

import { ApiError } from "@/services/api";

/**
 * Map server-side validation errors (422) onto react-hook-form fields.
 * Returns true when at least one error was attached to a field.
 */
export function applyApiFieldErrors<T extends FieldValues>(
  error: unknown,
  setError: UseFormSetError<T>,
  rename: Record<string, string> = {},
): boolean {
  if (!(error instanceof ApiError) || error.fieldErrors.length === 0) return false;
  let applied = false;
  for (const fieldError of error.fieldErrors) {
    if (!fieldError.field) continue;
    const [head, ...rest] = fieldError.field.split(".");
    const name = [rename[head] ?? head, ...rest].join(".");
    setError(name as Path<T>, { type: "server", message: fieldError.message });
    applied = true;
  }
  return applied;
}
