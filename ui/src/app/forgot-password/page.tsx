"use client";

import { useActionState } from "react";

import { type ForgotPasswordState, forgotPassword } from "@/app/actions/auth";

export default function ForgotPasswordPage() {
  const [state, action, pending] = useActionState<
    ForgotPasswordState,
    FormData
  >(forgotPassword, undefined);

  if (state?.sent) {
    return (
      <div className="flex min-h-full items-center justify-center bg-zinc-50 px-4">
        <div className="w-full max-w-sm space-y-4 text-center">
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
            Revisá tu email
          </h1>
          <p className="text-sm text-zinc-500">
            Si existe una cuenta asociada a ese email, te enviamos un enlace
            para restablecer tu contraseña.
          </p>
          <a
            href="/login"
            className="block text-sm text-zinc-500 underline hover:text-zinc-700"
          >
            Volver al inicio de sesión
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-full items-center justify-center bg-zinc-50 px-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center">
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
            Recuperar contraseña
          </h1>
          <p className="mt-1 text-sm text-zinc-500">
            Ingresá tu email UNQ y te enviamos un enlace de recuperación.
          </p>
        </div>

        <form action={action} className="space-y-4">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-zinc-700"
            >
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              autoComplete="email"
              placeholder="usuario@unq.edu.ar"
              className="mt-1 block w-full rounded-md border border-zinc-300 px-3 py-2 text-sm placeholder-zinc-400 focus:border-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-900"
            />
          </div>

          {state?.error && (
            <p className="text-sm text-red-600">{state.error}</p>
          )}

          <button
            type="submit"
            disabled={pending}
            className="w-full rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
          >
            {pending ? "Enviando..." : "Enviar enlace"}
          </button>
        </form>

        <p className="text-center text-sm text-zinc-500">
          <a href="/login" className="underline hover:text-zinc-700">
            Volver al inicio de sesión
          </a>
        </p>
      </div>
    </div>
  );
}
