"use client";
import { useState } from "react";

import * as admin from "@/lib/api/admin";

export function useInviteUser() {
	const [email, setEmail] = useState("");
	const [role, setRole] = useState<admin.UserRole | "">("");
	const [pending, setPending] = useState(false);
	const [error, setError] = useState<string | undefined>();
	const [success, setSuccess] = useState<string | undefined>();

	async function handleSubmit() {
		if (!role) return;

		setError(undefined);
		setSuccess(undefined);
		setPending(true);

		const result = await admin.inviteUser(email, role);
		setPending(false);

		if (result.ok) {
			setSuccess(`Invitación enviada a ${email}`);
			setEmail("");
			setRole("");
			return;
		}

		setError(result.error);
	}

	return {
		email,
		setEmail,
		role,
		setRole,
		pending,
		error,
		success,
		handleSubmit,
	};
}
