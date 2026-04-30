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
  const segments = pathname.split("/").filter(Boolean);
  const isProjectRoute = segments[0] === "projects" && Boolean(segments[1]);
  const projectId = isProjectRoute ? segments[1] : null;

  const breadcrumbs = buildBreadcrumbs(segments);

  const projectNavItems = projectId
    ? [
        { href: `/projects/${projectId}`, label: "Overview" },
        { href: `/projects/${projectId}/characters`, label: "Characters" },
        { href: `/projects/${projectId}/style`, label: "Style" },
        { href: `/projects/${projectId}/pages`, label: "Pages" }
      ]
    : [];

  const showBackToCharacters = isProjectRoute && segments[2] === "characters" && Boolean(segments[3]);
  const showBackToPages = isProjectRoute && segments[2] === "pages" && Boolean(segments[3]);

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
      <section className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <nav className="card flex flex-wrap items-center gap-1 px-3 py-2 text-sm">
          {breadcrumbs.map((crumb, idx) => (
            <span key={crumb.href} className="flex items-center gap-1">
              <Link
                href={crumb.href}
                className={`rounded-md px-2 py-1 transition ${
                  pathname === crumb.href ? "bg-[#eaf6ef] font-bold text-[#1d5b36]" : "text-[#6e5b49] hover:bg-[#fff6e6]"
                }`}
              >
                {crumb.label}
              </Link>
              {idx < breadcrumbs.length - 1 && <span className="text-[#a18d77]">/</span>}
            </span>
          ))}
        </nav>

        <div className="flex flex-wrap gap-2">
          {showBackToCharacters && projectId && (
            <Link href={`/projects/${projectId}/characters`} className="btn btn-outline">
              Back to Characters
            </Link>
          )}
          {showBackToPages && projectId && (
            <Link href={`/projects/${projectId}/pages`} className="btn btn-outline">
              Back to Pages
            </Link>
          )}
        </div>
      </section>
      {isProjectRoute && projectId && (
        <section className="card mb-5 flex flex-wrap items-center gap-2 p-3">
          <p className="mr-2 text-sm font-bold text-[#665441]">Project Navigation</p>
          {projectNavItems.map((item) => {
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link key={item.href} href={item.href} className={`btn ${active ? "btn-primary" : "btn-outline"}`}>
                {item.label}
              </Link>
            );
          })}
        </section>
      )}
      <main>{children}</main>
    </div>
  );
}

function buildBreadcrumbs(segments: string[]) {
  const crumbs: Array<{ href: string; label: string }> = [{ href: "/", label: "Dashboard" }];

  if (segments.length === 0) {
    return crumbs;
  }

  let currentPath = "";
  for (let i = 0; i < segments.length; i += 1) {
    const segment = segments[i];
    currentPath += `/${segment}`;
    crumbs.push({
      href: currentPath,
      label: breadcrumbLabel(segments, i)
    });
  }

  return crumbs;
}

function breadcrumbLabel(segments: string[], idx: number) {
  const segment = segments[idx];
  if (idx === 0 && segment === "projects") return "Projects";
  if (idx === 1 && segments[0] === "projects") return `Project ${segment}`;
  if (segment === "characters") return "Characters";
  if (segment === "style") return "Style Profile";
  if (segment === "pages") return "Story Pages";
  if (idx === 3 && segments[2] === "pages") return `Page ${segment}`;
  if (idx === 3 && segments[2] === "characters") return `Character ${segment}`;
  return segment.charAt(0).toUpperCase() + segment.slice(1);
}
