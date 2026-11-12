export interface ApiEnvelope<T> {
  status: number;
  message: string;
  data: T | null;
}

export interface FieldError {
  field: string | null;
  message: string;
  type?: string;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
