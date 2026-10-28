import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useDebouncedValue } from "@/hooks/useDebouncedValue";

beforeEach(() => {
	vi.useFakeTimers();
});

afterEach(() => {
	vi.useRealTimers();
});

describe("useDebouncedValue", () => {
	it("retrasa el valor hasta que pasa el delay", () => {
		const { result, rerender } = renderHook(
			({ value }) => useDebouncedValue(value, 300),
			{ initialProps: { value: "a" } },
		);

		rerender({ value: "ab" });
		expect(result.current).toBe("a");

		act(() => vi.advanceTimersByTime(299));
		expect(result.current).toBe("a");

		act(() => vi.advanceTimersByTime(1));
		expect(result.current).toBe("ab");
	});

	it("descarta el valor intermedio si llega otro antes del delay", () => {
		const { result, rerender } = renderHook(
			({ value }) => useDebouncedValue(value, 300),
			{ initialProps: { value: "" } },
		);

		rerender({ value: "ga" });
		act(() => vi.advanceTimersByTime(200));
		rerender({ value: "gar" });
		act(() => vi.advanceTimersByTime(299));
		expect(result.current).toBe("");

		act(() => vi.advanceTimersByTime(1));
		expect(result.current).toBe("gar");
	});
});
