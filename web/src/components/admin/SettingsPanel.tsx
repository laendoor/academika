"use client";
import { SettingsTable } from "@/components/admin/SettingsTable";
import { ErrorState, LoadingState } from "@/components/ui/PageState";
import { useAdminSettings } from "@/hooks/admin";

export function SettingsPanel() {
	const { settings, loading, error, updating, handleUpdate } =
		useAdminSettings();

	if (loading) return <LoadingState />;
	if (error) return <ErrorState error={error} />;

	return (
		<SettingsTable
			settings={settings}
			updating={updating}
			onUpdate={handleUpdate}
		/>
	);
}
