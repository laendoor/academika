import type { ReactNode } from "react";

export function AuthFooterLink({
  href,
  children,
}: {
  href: string;
  children: ReactNode;
}) {
  return (
    <p className="text-center text-sm text-zinc-500">
      <a href={href} className="underline hover:text-zinc-700">
        {children}
      </a>
    </p>
  );
}
