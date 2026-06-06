export default function WorkspacePage() {
  return (
    <div className="flex min-h-full items-center justify-center">
      <div className="space-y-4 text-center">
        <p className="text-zinc-500">Workspace - coming soon</p>
        <a
          href="/api/auth/signout"
          className="text-sm text-zinc-400 underline hover:text-zinc-600"
        >
          Sign out
        </a>
      </div>
    </div>
  );
}
