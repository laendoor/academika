import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { SettingsTable } from "@/components/admin/SettingsTable";
import type { SettingItem } from "@/lib/api/admin";

const SETTINGS: SettingItem[] = [
	{
		key: "auth.allowed_domains",
		value: ["@unq.edu.ar"],
		description: "Dominios habilitados",
	},
];

describe("SettingsTable", () => {
	it("muestra clave, descripción y valor como JSON", () => {
		render(
			<SettingsTable settings={SETTINGS} updating={null} onUpdate={vi.fn()} />,
		);

		expect(screen.getByText("auth.allowed_domains")).toBeDefined();
		expect(screen.getByDisplayValue('["@unq.edu.ar"]')).toBeDefined();
	});

	it("llama onUpdate con el valor parseado al guardar", () => {
		const onUpdate = vi.fn();
		render(
			<SettingsTable settings={SETTINGS} updating={null} onUpdate={onUpdate} />,
		);

		fireEvent.change(screen.getByDisplayValue('["@unq.edu.ar"]'), {
			target: { value: "[]" },
		});
		fireEvent.click(screen.getByRole("button", { name: "Guardar" }));

		expect(onUpdate).toHaveBeenCalledWith("auth.allowed_domains", []);
	});

	it("muestra error y no llama onUpdate con JSON inválido", () => {
		const onUpdate = vi.fn();
		render(
			<SettingsTable settings={SETTINGS} updating={null} onUpdate={onUpdate} />,
		);

		fireEvent.change(screen.getByDisplayValue('["@unq.edu.ar"]'), {
			target: { value: "[roto" },
		});
		fireEvent.click(screen.getByRole("button", { name: "Guardar" }));

		expect(screen.getByText("JSON inválido")).toBeDefined();
		expect(onUpdate).not.toHaveBeenCalled();
	});

	it("deshabilita guardar sin cambios", () => {
		render(
			<SettingsTable settings={SETTINGS} updating={null} onUpdate={vi.fn()} />,
		);

		expect(
			screen.getByRole("button", { name: "Guardar" }) as HTMLButtonElement,
		).toHaveProperty("disabled", true);
	});
});
