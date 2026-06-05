"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { AuthCard } from "@/components/auth/AuthCard";
import { AuthFooterLink } from "@/components/auth/AuthFooterLink";
import { AuthHeader } from "@/components/auth/AuthHeader";
import { FormButton } from "@/components/auth/FormButton";
import { FormError } from "@/components/auth/FormError";
import { FormField } from "@/components/auth/FormField";
import { login } from "@/lib/api/auth";

export default function LoginPage() {
	const [error, setError] = useState<string | undefined>();
	const [pending, setPending] = useState(false);
	const router = useRouter();

	async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
		e.preventDefault();
		setPending(true);
		setError(undefined);

		const formData = new FormData(e.currentTarget);
		const result = await login(
			formData.get("email") as string,
			formData.get("password") as string,
		);

		if (result.ok) {
			router.push("/");
			return;
		}

		setError(result.error);
		setPending(false);
	}

	return (
		<AuthCard>
			<AuthHeader
				title="Académika"
				subtitle="Iniciá sesión con tu cuenta UNQ"
			/>
			<form onSubmit={handleSubmit} className="space-y-4">
				<FormField
					id="email"
					name="email"
					label="Email"
					type="email"
					required
					autoComplete="email"
					placeholder="usuario@unq.edu.ar"
				/>
				<FormField
					id="password"
					name="password"
					label="Contraseña"
					type="password"
					required
					autoComplete="current-password"
				/>
				<FormError error={error} />
				<FormButton
					pending={pending}
					label="Ingresar"
					pendingLabel="Ingresando..."
				/>
			</form>
			<AuthFooterLink href="/forgot-password">
				¿Olvidaste tu contraseña?
			</AuthFooterLink>
		</AuthCard>
	);
}
