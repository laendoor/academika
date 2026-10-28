"use client";
import { useEffect, useState } from "react";

/** Retrasa el valor para que un input de búsqueda no dispare un request por tecla. */
export function useDebouncedValue<T>(value: T, delay = 300): T {
	const [debounced, setDebounced] = useState(value);

	useEffect(() => {
		const timer = setTimeout(() => setDebounced(value), delay);
		return () => clearTimeout(timer);
	}, [value, delay]);

	return debounced;
}
