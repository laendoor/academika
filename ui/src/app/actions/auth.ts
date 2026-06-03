"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { API_URL, IS_PRODUCTION } from "@/lib/constants";

// --- Types ---

export type LoginState = { error?: string } | undefined;

export type ForgotPasswordState =
  | { sent?: boolean; error?: string }
  | undefined;

export type ResetPasswordState = { error?: string } | undefined;

// --- Constants ---

const UNEXPECTED_ERROR = "Error inesperado. Intentá de nuevo más tarde.";

// --- Actions ---

export async function login(
  _state: LoginState,
  formData: FormData,
): Promise<LoginState> {
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;

  const res = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    if (res.status === 401) {
      const body = await res.json();
      return { error: body.detail as string };
    }
    return { error: UNEXPECTED_ERROR };
  }

  const { access_token, refresh_token } = await res.json();
  const cookieStore = await cookies();

  const secure = IS_PRODUCTION;

  cookieStore.set("access_token", access_token, {
    httpOnly: true,
    secure,
    sameSite: "lax",
    maxAge: 15 * 60,
    path: "/",
  });
  cookieStore.set("refresh_token", refresh_token, {
    httpOnly: true,
    secure,
    sameSite: "lax",
    maxAge: 7 * 24 * 60 * 60,
    path: "/",
  });

  redirect("/");
}

export async function logout() {
  const cookieStore = await cookies();
  cookieStore.delete("access_token");
  cookieStore.delete("refresh_token");
  redirect("/login");
}

export async function forgotPassword(
  _state: ForgotPasswordState,
  formData: FormData,
): Promise<ForgotPasswordState> {
  const email = formData.get("email") as string;

  const res = await fetch(`${API_URL}/api/v1/auth/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  if (res.ok || res.status === 204) {
    return { sent: true };
  }

  return { error: UNEXPECTED_ERROR };
}

export async function resetPassword(
  _state: ResetPasswordState,
  formData: FormData,
): Promise<ResetPasswordState> {
  const token = formData.get("token") as string;
  const newPassword = formData.get("new_password") as string;

  const res = await fetch(`${API_URL}/api/v1/auth/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password: newPassword }),
  });

  if (res.ok || res.status === 204) {
    redirect("/login");
  }

  if (res.status === 401) {
    const body = await res.json();
    return { error: body.detail as string };
  }

  return { error: UNEXPECTED_ERROR };
}
