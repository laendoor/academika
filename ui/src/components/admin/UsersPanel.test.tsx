import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { UsersPanel } from "@/components/admin/UsersPanel";
import { useAdminUsers } from "@/hooks/admin";
import type { UserItem } from "@/lib/api/admin";

vi.mock("@/hooks/admin", () => ({ useAdminUsers: vi.fn() }));

const useAdminUsersMock = vi.mocked(useAdminUsers);

function makeUser(): UserItem {
	return {
		id: "u1",
		email: "a@unq.edu.ar",
		role: "director",
		is_active: true,
		created_at: "2026-01-01T00:00:00Z",
		updated_at: "2026-01-01T00:00:00Z",
	};
}

describe("UsersPanel", () => {
	it("muestra loading", () => {
		useAdminUsersMock.mockReturnValue({
			users: [],
			loading: true,
			error: undefined,
			updating: null,
			handleUpdate: vi.fn(),
		});
		render(<UsersPanel />);
		expect(screen.getByText("Cargando...")).toBeInTheDocument();
	});

	it("muestra error", () => {
		useAdminUsersMock.mockReturnValue({
			users: [],
			loading: false,
			error: "no autorizado",
			updating: null,
			handleUpdate: vi.fn(),
		});
		render(<UsersPanel />);
		expect(screen.getByText("no autorizado")).toBeInTheDocument();
	});

	it("muestra la tabla con usuarios", () => {
		useAdminUsersMock.mockReturnValue({
			users: [makeUser()],
			loading: false,
			error: undefined,
			updating: null,
			handleUpdate: vi.fn(),
		});
		render(<UsersPanel />);
		expect(screen.getByText("a@unq.edu.ar")).toBeInTheDocument();
	});
});
