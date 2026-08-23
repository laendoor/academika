import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useForgotPasswordForm } from "@/hooks/auth/useForgotPasswordForm";

const { forgotPasswordMock } = vi.hoisted(() => ({
	forgotPasswordMock: vi.fn(),
}));

vi.mock("@/lib/api/auth", () => ({ forgotPassword: forgotPasswordMock }));

function makeForm(email: string): FormData {
	const fd = new FormData();
	fd.set("email", email);
	return fd;
}

describe("useForgotPasswordForm", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("marca sent al éxito", async () => {
		forgotPasswordMock.mockResolvedValue({ ok: true, data: { sent: true } });

		const { result } = renderHook(() => useForgotPasswordForm());

		await act(async () => {
			await result.current.handleAction(makeForm("a@unq.edu.ar"));
		});

		expect(forgotPasswordMock).toHaveBeenCalledWith("a@unq.edu.ar");
		expect(result.current.sent).toBe(true);
		expect(result.current.error).toBeUndefined();
	});

	it("setea error al fallar", async () => {
		forgotPasswordMock.mockResolvedValue({ ok: false, error: "no existe" });

		const { result } = renderHook(() => useForgotPasswordForm());

		await act(async () => {
			await result.current.handleAction(makeForm("a@unq.edu.ar"));
		});

		expect(result.current.sent).toBe(false);
		expect(result.current.error).toBe("no existe");
	});
});
