import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Combobox } from "@/components/ui/Combobox";
import type { SearchHit } from "@/lib/api/search";

const HITS: SearchHit[] = [
	{ id: "a1", label: "Núñez, Lucía · DNI 33333333", term: "Núñez Lucía" },
	{ id: "a2", label: "Fernández, Ana · DNI 44444444", term: "Fernández Ana" },
];

function renderCombobox(onChange = vi.fn(), hits: SearchHit[] = HITS) {
	render(
		<Combobox
			label="Filtrar por alumno"
			placeholder="Alumno (DNI o nombre)"
			value=""
			onChange={onChange}
			suggestions={hits}
		/>,
	);
	return { input: screen.getByLabelText("Filtrar por alumno"), onChange };
}

describe("Combobox", () => {
	it("no muestra la lista hasta que se escribe", () => {
		renderCombobox();

		expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
	});

	it("muestra las sugerencias al escribir", () => {
		const { input } = renderCombobox();

		fireEvent.change(input, { target: { value: "lu" } });

		expect(screen.getByRole("listbox")).toBeInTheDocument();
		expect(screen.getAllByRole("option")).toHaveLength(2);
		expect(input).toHaveAttribute("aria-expanded", "true");
	});

	it("elegir con Enter escribe el término del hit", () => {
		const { input, onChange } = renderCombobox();
		fireEvent.change(input, { target: { value: "lu" } });

		fireEvent.keyDown(input, { key: "ArrowDown" });
		expect(screen.getAllByRole("option")[0]).toHaveAttribute(
			"aria-selected",
			"true",
		);
		fireEvent.keyDown(input, { key: "Enter" });

		expect(onChange).toHaveBeenLastCalledWith("Núñez Lucía");
		expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
	});

	it("las flechas recorren la lista y dan la vuelta", () => {
		const { input, onChange } = renderCombobox();
		fireEvent.change(input, { target: { value: "lu" } });

		fireEvent.keyDown(input, { key: "ArrowUp" });
		expect(screen.getAllByRole("option")[1]).toHaveAttribute(
			"aria-selected",
			"true",
		);
		fireEvent.keyDown(input, { key: "ArrowDown" });
		expect(screen.getAllByRole("option")[0]).toHaveAttribute(
			"aria-selected",
			"true",
		);
		expect(onChange).toHaveBeenCalledTimes(1);
	});

	it("elegir con el mouse escribe el término y cierra la lista", () => {
		const { input, onChange } = renderCombobox();
		fireEvent.change(input, { target: { value: "lu" } });

		fireEvent.click(screen.getByText("Fernández, Ana · DNI 44444444"));

		expect(onChange).toHaveBeenLastCalledWith("Fernández Ana");
		expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
	});

	it("Escape cierra la lista sin elegir", () => {
		const { input, onChange } = renderCombobox();
		fireEvent.change(input, { target: { value: "lu" } });

		fireEvent.keyDown(input, { key: "Escape" });

		expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
		expect(onChange).toHaveBeenCalledTimes(1);
	});

	it("la cruz limpia el filtro", () => {
		const onChange = vi.fn();
		render(
			<Combobox
				label="Filtrar por alumno"
				placeholder="Alumno (DNI o nombre)"
				value="Núñez Lucía"
				onChange={onChange}
				suggestions={HITS}
			/>,
		);

		fireEvent.click(screen.getByRole("button", { name: "Limpiar filtro" }));

		expect(onChange).toHaveBeenCalledWith("");
		expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
	});

	it("sin texto no hay cruz de limpiar", () => {
		renderCombobox();

		expect(
			screen.queryByRole("button", { name: "Limpiar filtro" }),
		).not.toBeInTheDocument();
	});

	it("sin sugerencias no abre la lista", () => {
		const { input } = renderCombobox(vi.fn(), []);

		fireEvent.change(input, { target: { value: "zzz" } });

		expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
	});
});
