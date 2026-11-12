import type { AuthPayload } from "@/types/user";

import { api } from "./api";

export interface LoginInput {
  email: string;
  password: string;
}

export interface RegisterInput extends LoginInput {
  name: string;
}

export const authService = {
  login: (input: LoginInput) =>
    api.post<AuthPayload>("/auth/login", input, { silentUnauthorized: true }),
  register: (input: RegisterInput) => api.post<AuthPayload>("/auth/register", input),
  logout: () => api.post<null>("/auth/logout"),
};
