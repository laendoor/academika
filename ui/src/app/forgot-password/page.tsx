"use client";

import { useActionState } from "react";

import { type ForgotPasswordState, forgotPassword } from "@/app/actions/auth";
import { AuthCard } from "@/components/auth/AuthCard";
import { AuthFooterLink } from "@/components/auth/AuthFooterLink";
import { AuthHeader } from "@/components/auth/AuthHeader";
import { FormButton } from "@/components/auth/FormButton";
import { FormError } from "@/components/auth/FormError";
import { FormField } from "@/components/auth/FormField";

function EmailSentConfirmation() {
  return (
    <AuthCard className="space-y-4 text-center">
      <AuthHeader
        title="Revisá tu email"
        subtitle="Si existe una cuenta asociada a ese email, te enviamos un enlace para restablecer tu contraseña."
      />
      <AuthFooterLink href="/login">Volver al inicio de sesión</AuthFooterLink>
    </AuthCard>
  );
}

export default function ForgotPasswordPage() {
  const [state, action, pending] = useActionState<
    ForgotPasswordState,
    FormData
  >(forgotPassword, undefined);

  if (state?.sent) return <EmailSentConfirmation />;

  return (
    <AuthCard>
      <AuthHeader
        title="Recuperar contraseña"
        subtitle="Ingresá tu email UNQ y te enviamos un enlace de recuperación."
      />
      <form action={action} className="space-y-4">
        <FormField
          id="email"
          name="email"
          label="Email"
          type="email"
          required
          autoComplete="email"
          placeholder="usuario@unq.edu.ar"
        />
        <FormError error={state?.error} />
        <FormButton
          pending={pending}
          label="Enviar enlace"
          pendingLabel="Enviando..."
        />
      </form>
      <AuthFooterLink href="/login">Volver al inicio de sesión</AuthFooterLink>
    </AuthCard>
  );
}
