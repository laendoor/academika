import { Sidebar } from "@/components/workspace/Sidebar";

export default function WorkspaceLayout({
	children,
}: Readonly<{ children: React.ReactNode }>) {
	return (
		<div className="flex flex-1">
			<Sidebar />
			<main className="flex-1">{children}</main>
		</div>
	);
}
