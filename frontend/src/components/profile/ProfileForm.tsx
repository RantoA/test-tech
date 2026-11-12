"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

import { Button } from "@/components/ui/Button";
import { FormField, Input } from "@/components/ui/Field";
import { useAuth } from "@/hooks/useAuth";
import { profileSchema, type ProfileValues } from "@/schemas/user.schema";
import { ApiError, getErrorMessage } from "@/services/api";
import { userService } from "@/services/user.service";
import type { User } from "@/types/user";
import { applyApiFieldErrors } from "@/utils/form-errors";

export function ProfileForm({ user }: { user: User }) {
  const { setUser } = useAuth();
  const {
    register,
    handleSubmit,
    setError,
    reset,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<ProfileValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: { name: user.name, email: user.email },
  });

  const onSubmit = handleSubmit(async (values) => {
    try {
      const updated = await userService.updateProfile(values);
      setUser(updated);
      reset({ name: updated.name, email: updated.email });
      toast.success("Profile updated");
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        setError("email", { type: "server", message: error.message });
      } else if (!applyApiFieldErrors(error, setError)) {
        toast.error(getErrorMessage(error));
      }
    }
  });

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-5">
      <FormField id="name" label="Full name" error={errors.name?.message}>
        <Input id="name" autoComplete="name" invalid={!!errors.name} {...register("name")} />
      </FormField>
      <FormField id="email" label="Email" error={errors.email?.message}>
        <Input id="email" type="email" autoComplete="email" invalid={!!errors.email} {...register("email")} />
      </FormField>
      <div className="flex justify-end">
        <Button type="submit" loading={isSubmitting} disabled={!isDirty}>
          Save changes
        </Button>
      </div>
    </form>
  );
}
