import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ImportPlanillas } from "@/components/admin/ImportPlanillas";
import { useAdminImport } from "@/hooks/admin";

vi.mock("@/hooks/admin", () => ({ useAdminImport: vi.fn() }));

const useAdminImportMock = vi.mocked(useAdminImport);

function makeImport(overrides: Record<string, unknown> = {}) {
	return {
		uploading: false,
		items: [],
		total: 0,
		loading: false,
		error: undefined,
		handleUpload: vi.fn(),
		refresh: vi.fn(),
		...overrides,
	};
}

describe("ImportPlanillas", () => {
	it("deshabilita submit sin archivos", () => {
		useAdminImportMock.mockReturnValue(makeImport());
		render(<ImportPlanillas />);
		expect(
			screen.getByRole("button", { name: "Subir planillas" }),
		).toBeDisabled();
	});

	it("muestra mensaje vacío", () => {
		useAdminImportMock.mockReturnValue(makeImport());
		render(<ImportPlanillas />);
		expect(
			screen.getByText("Sin importaciones registradas todavía."),
		).toBeInTheDocument();
	});

	it("muestra Subiendo... cuando está subiendo", () => {
		useAdminImportMock.mockReturnValue(makeImport({ uploading: true }));
		render(<ImportPlanillas />);
		expect(screen.getByRole("button", { name: "Subiendo..." })).toBeDisabled();
	});

	it("llama handleUpload al enviar archivos", () => {
		const handleUpload = vi.fn();
		useAdminImportMock.mockReturnValue(makeImport({ handleUpload }));
		const { container } = render(<ImportPlanillas />);

		const file = new File(["x"], "alumnos.csv");
		const input = container.querySelector(
			'input[type="file"]',
		) as HTMLInputElement;
		fireEvent.change(input, { target: { files: [file] } });

		const form = container.querySelector("form") as HTMLFormElement;
		fireEvent.submit(form);

		expect(handleUpload).toHaveBeenCalledWith([file]);
	});
});
