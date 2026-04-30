"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

const navItems = [
  { href: "/", label: "Dashboard" },
  { href: "/projects", label: "Projects" }
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="mx-auto min-h-screen max-w-7xl px-4 py-5 sm:px-6 lg:px-8">
      <header className="card mb-5 flex flex-wrap items-center justify-between gap-3 p-4">
        <div>
          <p className="text-sm text-[#7d6a57]">BoardBook Studio</p>
          <h1 style={{ fontFamily: "var(--font-heading)" }} className="text-2xl">
            Children&apos;s Illustration Assistant
          </h1>
        </div>
        <nav className="flex gap-2">
          {navItems.map((item) => {
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`btn ${active ? "btn-primary" : "btn-outline"}`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </header>
      <main>{children}</main>
    </div>
  );
}
