"use client";
import { AuthCard } from "@/components/auth/AuthCard";
import { AuthFooterLink } from "@/components/auth/AuthFooterLink";
import { AuthHeader } from "@/components/auth/AuthHeader";
import { FormButton } from "@/components/auth/FormButton";
import { FormError } from "@/components/auth/FormError";
import { FormField } from "@/components/auth/FormField";
import { useLoginForm } from "@/hooks/auth";

export default function LoginPage() {
	const { handleAction, error, pending } = useLoginForm();

	return (
		<AuthCard>
			<AuthHeader
				title="Académika"
				subtitle="Iniciá sesión con tu cuenta UNQ"
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
