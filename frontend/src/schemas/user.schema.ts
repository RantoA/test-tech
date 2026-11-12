import { z } from "zod";

import { emailSchema, nameSchema, passwordSchema } from "./auth.schema";

export const profileSchema = z.object({
  name: nameSchema,
  email: emailSchema,
});

export const passwordChangeSchema = z
  .object({
    current_password: z.string().min(1, "Current password is required"),
    new_password: passwordSchema,
    confirm_password: z.string().min(1, "Please confirm the new password"),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  })
  .refine((data) => data.new_password !== data.current_password, {
    message: "New password must be different from the current one",
    path: ["new_password"],
  });

export type ProfileValues = z.infer<typeof profileSchema>;
export type PasswordChangeValues = z.infer<typeof passwordChangeSchema>;
