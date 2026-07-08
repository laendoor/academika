import { ImportPlanillas } from "@/components/admin/ImportPlanillas";
import { UsersPanel } from "@/components/admin/UsersPanel";
import { type TabItem, Tabs } from "@/components/ui/Tabs";

const ITEMS: TabItem[] = [
	{ label: "Usuarios", content: <UsersPanel /> },
	{ label: "Planillas", content: <ImportPlanillas /> },
];

export default function AdminPage() {
	return (
		<div className="p-8">
			<Tabs items={ITEMS} />
		</div>
	);
}
