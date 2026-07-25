import { AdminSidebar } from "@/components/admin/AdminSidebar";

export default function AdminLayout({
	children,
}: Readonly<{ children: React.ReactNode }>) {
	return (
		<div className="flex flex-1">
			<AdminSidebar />
			<main className="flex-1">{children}</main>
		</div>
	);
}
