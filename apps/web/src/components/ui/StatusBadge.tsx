export function StatusBadge({
	status,
}: {
	status: "ok" | "processing" | "error";
}) {
	const styles =
		status === "ok"
			? "bg-success/10 text-success"
			: status === "processing"
				? "bg-warning/5 text-warning"
				: "bg-danger/10 text-danger";
	const label =
		status === "ok" ? "OK" : status === "processing" ? "Procesando" : "Error";
	return (
		<span className={`rounded px-2 py-0.5 text-xs font-medium ${styles}`}>
			{label}
		</span>
	);
}
