import type { Metadata } from "next";
import { Baloo_2, Nunito } from "next/font/google";
import type { ReactNode } from "react";

import "./globals.css";
import { AppShell } from "@/components/app-shell";

const heading = Baloo_2({ subsets: ["latin"], variable: "--font-heading" });
const body = Nunito({ subsets: ["latin"], variable: "--font-body" });

export const metadata: Metadata = {
  title: "BoardBook Studio",
  description: "Local-first board-book illustration assistant"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={`${heading.variable} ${body.variable}`}>
      <body style={{ fontFamily: "var(--font-body)" }}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
