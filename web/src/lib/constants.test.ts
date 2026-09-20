import { describe, expect, it } from "vitest";

import { buildWsUrl } from "@/lib/constants";

describe("buildWsUrl", () => {
	it("usa wss para https", () => {
		expect(buildWsUrl({ protocol: "https:", host: "unq.edu.ar" })).toBe(
			"wss://unq.edu.ar/ws",
		);
	});

	it("usa ws para http", () => {
		expect(buildWsUrl({ protocol: "http:", host: "unq.edu.ar" })).toBe(
			"ws://unq.edu.ar/ws",
		);
	});
});
