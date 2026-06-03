"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { API_URL, IS_PRODUCTION } from "@/lib/constants";

export type LoginState = { error?: string } | undefined;

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
    return { error: "Error inesperado. Intentá de nuevo más tarde." };
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
