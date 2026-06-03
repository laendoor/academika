"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useActionState } from "react";

import { type ResetPasswordState, resetPassword } from "@/app/actions/auth";

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";

  const [state, action, pending] = useActionState<ResetPasswordState, FormData>(
    resetPassword,
    undefined,
  );

  if (!token) {
    return (
      <div className="w-full max-w-sm space-y-4 text-center">
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
          Enlace inválido
        </h1>
        <p className="text-sm text-zinc-500">
          El enlace de recuperación es inválido o expiró.
        </p>
        <a
          href="/forgot-password"
          className="block text-sm text-zinc-500 underline hover:text-zinc-700"
        >
          Solicitar un nuevo enlace
        </a>
      </div>
    );
  }

  return (
    <div className="w-full max-w-sm space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
          Nueva contraseña
        </h1>
        <p className="mt-1 text-sm text-zinc-500">
          Ingresá tu nueva contraseña para Académika.
        </p>
      </div>

      <form action={action} className="space-y-4">
        <input type="hidden" name="token" value={token} />

        <div>
          <label
            htmlFor="new_password"
            className="block text-sm font-medium text-zinc-700"
          >
            Nueva contraseña
          </label>
          <input
            id="new_password"
            name="new_password"
            type="password"
            required
            autoComplete="new-password"
            className="mt-1 block w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-900"
          />
        </div>

        {state?.error && <p className="text-sm text-red-600">{state.error}</p>}

        <button
          type="submit"
          disabled={pending}
          className="w-full rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
        >
          {pending ? "Guardando..." : "Guardar contraseña"}
        </button>
      </form>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="flex min-h-full items-center justify-center bg-zinc-50 px-4">
      <Suspense>
        <ResetPasswordForm />
      </Suspense>
    </div>
  );
}
