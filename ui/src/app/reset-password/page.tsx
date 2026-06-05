"use client";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { AuthCard } from "@/components/auth/AuthCard";
import { AuthFooterLink } from "@/components/auth/AuthFooterLink";
import { AuthHeader } from "@/components/auth/AuthHeader";
import { FormButton } from "@/components/auth/FormButton";
import { FormError } from "@/components/auth/FormError";
import { FormField } from "@/components/auth/FormField";
import { resetPassword } from "@/lib/api/auth";

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
	const router = useRouter();

	const [error, setError] = useState<string | undefined>();
	const [pending, setPending] = useState(false);

	if (!token) return <InvalidResetToken />;

	async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
		e.preventDefault();
		setPending(true);
		setError(undefined);

		const formData = new FormData(e.currentTarget);
		const result = await resetPassword(
			token,
			formData.get("new_password") as string,
		);

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
				title="Nueva contraseña"
				subtitle="Ingresá tu nueva contraseña para Académika."
			/>
			<form onSubmit={handleSubmit} className="space-y-4">
				<FormField
					id="new_password"
					name="new_password"
					label="Nueva contraseña"
					type="password"
					required
					autoComplete="new-password"
				/>
				<FormError error={error} />
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
