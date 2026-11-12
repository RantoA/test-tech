import type { ApiEnvelope, FieldError } from "@/types/api";
import { CSRF_COOKIE, CSRF_HEADER, getCookie } from "@/utils/cookies";

export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8005/api/v1").replace(
  /\/$/,
  "",
);

export const UNAUTHORIZED_EVENT = "auth:unauthorized";

export class ApiError extends Error {
  readonly status: number;
  readonly fieldErrors: FieldError[];

  constructor(status: number, message: string, fieldErrors: FieldError[] = []) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.fieldErrors = fieldErrors;
  }
}

type Method = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
type Query = Record<string, string | number | boolean | undefined | null>;

interface RequestOptions {
  body?: unknown;
  query?: Query;
  signal?: AbortSignal;
  /** Do not broadcast 401 responses (e.g. login form, session probe). */
  silentUnauthorized?: boolean;
}

function buildUrl(path: string, query?: Query): string {
  const url = new URL(`${API_URL}${path}`);
  Object.entries(query ?? {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") url.searchParams.set(key, String(value));
  });
  return url.toString();
}

async function request<T>(method: Method, path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  let body: BodyInit | undefined;

  if (options.body instanceof FormData) {
    body = options.body; // the browser sets the multipart boundary itself
  } else if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(options.body);
  }

  if (method !== "GET") {
    const csrf = getCookie(CSRF_COOKIE);
    if (csrf) headers[CSRF_HEADER] = csrf;
  }

  let response: Response;
  try {
    response = await fetch(buildUrl(path, options.query), {
      method,
      headers,
      body,
      credentials: "include",
      signal: options.signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ApiError(0, "Unable to reach the server. Please check your connection.");
  }

  if (response.status === 204) return undefined as T;

  let envelope: ApiEnvelope<unknown> | null = null;
  try {
    envelope = (await response.json()) as ApiEnvelope<unknown>;
  } catch {
    envelope = null;
  }

  if (!response.ok) {
    const message = envelope?.message ?? "An unexpected error occurred.";
    const data = envelope?.data as { errors?: FieldError[] } | null | undefined;
    if (response.status === 401 && !options.silentUnauthorized && typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent(UNAUTHORIZED_EVENT));
    }
    throw new ApiError(response.status, message, data?.errors ?? []);
  }

  return (envelope?.data ?? undefined) as T;
}

export const api = {
  get: <T>(path: string, options?: RequestOptions) => request<T>("GET", path, options),
  post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>("POST", path, { ...options, body }),
  put: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>("PUT", path, { ...options, body }),
  patch: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>("PATCH", path, { ...options, body }),
  delete: <T>(path: string, options?: RequestOptions) => request<T>("DELETE", path, options),
};

export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return "An unexpected error occurred.";
}
