export function StatusBadge({
	status,
}: {
	status: "ok" | "processing" | "error";
}) {
	const styles =
		status === "ok"
			? "bg-green-100 text-green-700"
			: status === "processing"
				? "bg-yellow-100 text-yellow-700"
				: "bg-red-100 text-red-700";
	const label =
		status === "ok" ? "OK" : status === "processing" ? "Procesando" : "Error";
	return (
		<span className={`rounded px-2 py-0.5 text-xs font-medium ${styles}`}>
			{label}
		</span>
	);
}
