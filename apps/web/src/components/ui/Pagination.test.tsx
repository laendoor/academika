import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Pagination } from "@/components/ui/Pagination";

describe("Pagination", () => {
	it("no renderiza nada con una sola página", () => {
		const { container } = render(
			<Pagination
				skip={0}
				total={10}
				pageSize={20}
				loading={false}
				onChange={vi.fn()}
			/>,
		);
		expect(container).toBeEmptyDOMElement();
	});

	it("muestra el rango y navega", () => {
		const onChange = vi.fn();
		render(
			<Pagination
				skip={0}
				total={25}
				pageSize={20}
				loading={false}
				onChange={onChange}
			/>,
		);
		expect(screen.getByText("1-20 de 25")).toBeInTheDocument();
		expect(screen.getByRole("button", { name: "Anterior" })).toBeDisabled();
		fireEvent.click(screen.getByRole("button", { name: "Siguiente" }));
		expect(onChange).toHaveBeenCalledWith(20);
	});
});
