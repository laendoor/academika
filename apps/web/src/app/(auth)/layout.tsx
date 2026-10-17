import { SiteHeader } from "@/components/SiteHeader";

export default function AppLayout({
	children,
}: Readonly<{ children: React.ReactNode }>) {
	return (
		<>
			<SiteHeader />
			<main className="flex flex-1 flex-col">{children}</main>
		</>
	);
}
