"use client";

import { useState } from "react";

import { AuthCard } from "@/components/auth/AuthCard";
import { AuthFooterLink } from "@/components/auth/AuthFooterLink";
import { AuthHeader } from "@/components/auth/AuthHeader";
import { FormButton } from "@/components/auth/FormButton";
import { FormError } from "@/components/auth/FormError";
import { FormField } from "@/components/auth/FormField";
import { forgotPassword } from "@/lib/api/auth";

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
	const [sent, setSent] = useState(false);
	const [error, setError] = useState<string | undefined>();
	const [pending, setPending] = useState(false);

	if (sent) return <EmailSentConfirmation />;

	async function handleAction(formData: FormData) {
		setPending(true);
		setError(undefined);

		const result = await forgotPassword(formData.get("email") as string);

		if (result.ok) {
			setSent(true);
			return;
		}

		setError(result.error);
		setPending(false);
	}

	return (
		<AuthCard>
			<AuthHeader
				title="Recuperar contraseña"
				subtitle="Ingresá tu email UNQ y te enviamos un enlace de recuperación."
			/>
			<form action={handleAction} className="space-y-4">
				<FormField
					id="email"
					name="email"
					label="Email"
					type="email"
					required
					autoComplete="email"
					placeholder="usuario@unq.edu.ar"
				/>
				<FormError error={error} />
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
