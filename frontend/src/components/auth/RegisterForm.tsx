"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { FormField, Input } from "@/components/ui/Field";
import { useAuth } from "@/hooks/useAuth";
import { registerSchema, type RegisterValues } from "@/schemas/auth.schema";
import { ApiError, getErrorMessage } from "@/services/api";
import { applyApiFieldErrors } from "@/utils/form-errors";

export function RegisterForm() {
  const router = useRouter();
  const { register: registerAccount } = useAuth();
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<RegisterValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { name: "", email: "", password: "", confirmPassword: "" },
  });

  const onSubmit = handleSubmit(async ({ name, email, password }) => {
    setFormError(null);
    try {
      await registerAccount({ name, email, password });
      toast.success("Your account has been created");
      router.replace("/dashboard");
      router.refresh();
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        setError("email", { type: "server", message: error.message });
      } else if (!applyApiFieldErrors(error, setError)) {
        setFormError(getErrorMessage(error));
      }
    }
  });

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-5">
      {formError && <Alert>{formError}</Alert>}
      <FormField id="name" label="Full name" error={errors.name?.message}>
        <Input id="name" autoComplete="name" invalid={!!errors.name} {...register("name")} />
      </FormField>
      <FormField id="email" label="Email" error={errors.email?.message}>
        <Input id="email" type="email" autoComplete="email" invalid={!!errors.email} {...register("email")} />
      </FormField>
      <FormField
        id="password"
        label="Password"
        error={errors.password?.message}
        hint="At least 8 characters, including a letter and a digit."
      >
        <Input
          id="password"
          type="password"
          autoComplete="new-password"
          invalid={!!errors.password}
          {...register("password")}
        />
      </FormField>
      <FormField id="confirmPassword" label="Confirm password" error={errors.confirmPassword?.message}>
        <Input
          id="confirmPassword"
          type="password"
          autoComplete="new-password"
          invalid={!!errors.confirmPassword}
          {...register("confirmPassword")}
        />
      </FormField>
      <Button type="submit" className="w-full" loading={isSubmitting}>
        Create account
      </Button>
    </form>
  );
}
