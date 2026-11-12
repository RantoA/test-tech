import type { User } from "@/types/user";

import { api } from "./api";

export interface ProfileInput {
  name?: string;
  email?: string;
}

export interface PasswordInput {
  current_password: string;
  new_password: string;
}

export const userService = {
  me: (options?: { silentUnauthorized?: boolean }) => api.get<User>("/users/me", options),
  updateProfile: (input: ProfileInput) => api.put<User>("/users/me", input),
  changePassword: (input: PasswordInput) => api.patch<null>("/users/me/password", input),
};
