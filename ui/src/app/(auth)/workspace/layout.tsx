import { Group, Panel, Separator } from "react-resizable-panels";

import { ChatPanel } from "@/components/workspace/ChatPanel";
import { SourcesPanel } from "@/components/workspace/SourcesPanel";
import { StudioPanel } from "@/components/workspace/StudioPanel";

export default function WorkspaceLayout() {
	return (
		<Group orientation="horizontal" className="flex-1">
			<Panel defaultSize={30} minSize={20}>
				<div className="h-full overflow-y-auto border-r border-zinc-200">
					<SourcesPanel />
				</div>
			</Panel>
			<Separator className="w-0.5 bg-transparent transition-colors hover:bg-zinc-300" />
			<Panel defaultSize={40} minSize={25}>
				<ChatPanel />
			</Panel>
			<Separator className="w-0.5 bg-transparent transition-colors hover:bg-zinc-300" />
			<Panel defaultSize={30} minSize={20}>
				<div className="h-full overflow-y-auto border-l border-zinc-200">
					<StudioPanel />
				</div>
			</Panel>
		</Group>
	);
}
