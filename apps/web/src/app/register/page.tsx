"use client";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { AuthCard } from "@/components/auth/AuthCard";
import { AuthFooterLink } from "@/components/auth/AuthFooterLink";
import { AuthHeader } from "@/components/auth/AuthHeader";
import { FormButton } from "@/components/auth/FormButton";
import { FormError } from "@/components/auth/FormError";
import { FormField } from "@/components/auth/FormField";
import { useRegisterForm } from "@/hooks/auth";

function isTokenValid(token: string): boolean {
	try {
		const payload = JSON.parse(atob(token.split(".")[1]));
		return Date.now() / 1000 < (payload.exp ?? 0);
	} catch {
		return false;
	}
}

function InvalidInviteToken() {
	return (
		<AuthCard className="space-y-4 text-center">
			<AuthHeader
				title="Enlace inválido"
				subtitle="El enlace de invitación es inválido o expiró."
			/>
			<AuthFooterLink href="mailto:academika@unq.edu.ar">
				Contactá al administrador
			</AuthFooterLink>
		</AuthCard>
	);
}

function RegisterForm() {
	const searchParams = useSearchParams();
	const token = searchParams.get("token") ?? "";
	const { handleAction, error, pending } = useRegisterForm(token);

	if (!token || !isTokenValid(token)) return <InvalidInviteToken />;

	return (
		<AuthCard>
			<AuthHeader
				title="Crear cuenta"
				subtitle="Elegí una contraseña para acceder a Académika."
			/>
			<form action={handleAction} className="space-y-4">
				<FormField
					id="password"
					name="password"
					label="Contraseña"
					type="password"
					required
					autoComplete="new-password"
				/>
				<FormField
					id="confirm_password"
					name="confirm_password"
					label="Repetir contraseña"
					type="password"
					required
					autoComplete="new-password"
				/>
				<FormError error={error} />
				<FormButton
					pending={pending}
					label="Crear cuenta"
					pendingLabel="Creando cuenta..."
				/>
			</form>
		</AuthCard>
	);
}

export default function RegisterPage() {
	return (
		<Suspense>
			<RegisterForm />
		</Suspense>
	);
}
