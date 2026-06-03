"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useActionState } from "react";

import { type ResetPasswordState, resetPassword } from "@/app/actions/auth";
import { AuthCard } from "@/components/auth/AuthCard";
import { AuthFooterLink } from "@/components/auth/AuthFooterLink";
import { AuthHeader } from "@/components/auth/AuthHeader";
import { FormButton } from "@/components/auth/FormButton";
import { FormError } from "@/components/auth/FormError";
import { FormField } from "@/components/auth/FormField";

function InvalidResetToken() {
  return (
    <AuthCard className="space-y-4 text-center">
      <AuthHeader
        title="Enlace inválido"
        subtitle="El enlace de recuperación es inválido o expiró."
      />
      <AuthFooterLink href="/forgot-password">
        Solicitar un nuevo enlace
      </AuthFooterLink>
    </AuthCard>
  );
}

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";

  const [state, action, pending] = useActionState<ResetPasswordState, FormData>(
    resetPassword,
    undefined,
  );

  if (!token) return <InvalidResetToken />;

  return (
    <AuthCard>
      <AuthHeader
        title="Nueva contraseña"
        subtitle="Ingresá tu nueva contraseña para Académika."
      />
      <form action={action} className="space-y-4">
        <input type="hidden" name="token" value={token} />
        <FormField
          id="new_password"
          name="new_password"
          label="Nueva contraseña"
          type="password"
          required
          autoComplete="new-password"
        />
        <FormError error={state?.error} />
        <FormButton
          pending={pending}
          label="Guardar contraseña"
          pendingLabel="Guardando..."
        />
      </form>
    </AuthCard>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense>
      <ResetPasswordForm />
    </Suspense>
  );
}
