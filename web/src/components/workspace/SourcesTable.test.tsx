import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SourcesTable } from "@/components/workspace/SourcesTable";
import type { SourceItem } from "@/lib/api/sources";

function makeSource(overrides: Partial<SourceItem> = {}): SourceItem {
	return {
		id: "s1",
		created_at: "2026-01-01T00:00:00Z",
		status: "ok",
		details: {
			sheet_type: null,
			files: [],
			processed: 0,
			skipped: 0,
			error: null,
		},
		...overrides,
	};
}

describe("SourcesTable", () => {
	it("renderiza cabeceras", () => {
		render(<SourcesTable items={[]} />);
		expect(screen.getByText("Fecha")).toBeInTheDocument();
		expect(screen.getByText("Tipo")).toBeInTheDocument();
		expect(screen.getByText("Estado")).toBeInTheDocument();
	});

	it("traduce el tipo de planilla y muestra el estado", () => {
		render(
			<SourcesTable
				items={[
					makeSource({
						details: {
							sheet_type: "alumnos",
							files: ["a.csv"],
							processed: 10,
							skipped: 2,
							error: null,
						},
					}),
				]}
			/>,
		);

		expect(screen.getByText("Alumnos")).toBeInTheDocument();
		expect(screen.getByText("OK")).toBeInTheDocument();
		expect(screen.getByText("10")).toBeInTheDocument();
		expect(screen.getByText("2")).toBeInTheDocument();
	});

	it("muestra placeholder para tipo nulo y error", () => {
		render(
			<SourcesTable
				items={[
					makeSource({
						status: "error",
						details: {
							sheet_type: null,
							files: [],
							processed: 0,
							skipped: 0,
							error: "archivo corrupto",
						},
					}),
				]}
			/>,
		);

		expect(screen.getAllByText("Error")).toHaveLength(2);
		expect(screen.getByText("archivo corrupto")).toBeInTheDocument();
		expect(screen.getAllByText("—").length).toBeGreaterThan(0);
	});
});
