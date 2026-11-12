"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

import { Button } from "@/components/ui/Button";
import { FormField, Input } from "@/components/ui/Field";
import { passwordChangeSchema, type PasswordChangeValues } from "@/schemas/user.schema";
import { ApiError, getErrorMessage } from "@/services/api";
import { userService } from "@/services/user.service";
import { applyApiFieldErrors } from "@/utils/form-errors";

export function PasswordForm() {
  const {
    register,
    handleSubmit,
    setError,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<PasswordChangeValues>({
    resolver: zodResolver(passwordChangeSchema),
    defaultValues: { current_password: "", new_password: "", confirm_password: "" },
  });

  const onSubmit = handleSubmit(async ({ current_password, new_password }) => {
    try {
      await userService.changePassword({ current_password, new_password });
      reset();
      toast.success("Password updated");
    } catch (error) {
      if (error instanceof ApiError && error.status === 400) {
        setError("current_password", { type: "server", message: error.message });
      } else if (!applyApiFieldErrors(error, setError)) {
        toast.error(getErrorMessage(error));
      }
    }
  });

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-5">
      <FormField id="current_password" label="Current password" error={errors.current_password?.message}>
        <Input
          id="current_password"
          type="password"
          autoComplete="current-password"
          invalid={!!errors.current_password}
          {...register("current_password")}
        />
      </FormField>
      <FormField
        id="new_password"
        label="New password"
        error={errors.new_password?.message}
        hint="At least 8 characters, including a letter and a digit."
      >
        <Input
          id="new_password"
          type="password"
          autoComplete="new-password"
          invalid={!!errors.new_password}
          {...register("new_password")}
        />
      </FormField>
      <FormField id="confirm_password" label="Confirm new password" error={errors.confirm_password?.message}>
        <Input
          id="confirm_password"
          type="password"
          autoComplete="new-password"
          invalid={!!errors.confirm_password}
          {...register("confirm_password")}
        />
      </FormField>
      <div className="flex justify-end">
        <Button type="submit" loading={isSubmitting}>
          Update password
        </Button>
      </div>
    </form>
  );
}
