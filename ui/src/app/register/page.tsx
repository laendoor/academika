"use client";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { AuthCard } from "@/components/auth/AuthCard";
import { AuthFooterLink } from "@/components/auth/AuthFooterLink";
import { AuthHeader } from "@/components/auth/AuthHeader";
import { FormButton } from "@/components/auth/FormButton";
import { FormError } from "@/components/auth/FormError";
import { FormField } from "@/components/auth/FormField";
import { register } from "@/lib/api/auth";

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
	const router = useRouter();

	const [error, setError] = useState<string | undefined>();
	const [pending, setPending] = useState(false);

	if (!token) return <InvalidInviteToken />;

	async function handleAction(formData: FormData) {
		setError(undefined);

		const password = formData.get("password") as string;
		const confirmPassword = formData.get("confirm_password") as string;

		if (password !== confirmPassword) {
			setError("Las contraseñas no coinciden.");
			return;
		}

		setPending(true);
		const result = await register(token, password);

		if (result.ok) {
			router.push("/login");
			return;
		}

		setError(result.error);
		setPending(false);
	}

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
