import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ChatPanel } from "@/components/workspace/ChatPanel";

describe("ChatPanel", () => {
	it("renderiza el placeholder", () => {
		render(<ChatPanel />);
		expect(
			screen.getByText("Hari estará disponible próximamente"),
		).toBeInTheDocument();
	});
});
