"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";

type AppLayoutProps = {
  children: ReactNode;
};

const navItems = [
  { label: "\u30c0\u30c3\u30b7\u30e5\u30dc\u30fc\u30c9", href: "/" },
  { label: "\u30c1\u30e3\u30f3\u30cd\u30eb\u4e00\u89a7", href: "/channels" },
  { label: "\u30a2\u30ca\u30ea\u30c6\u30a3\u30af\u30b9", href: "/channels/demo" },
];

const copy = {
  dashboard: "\u30c0\u30c3\u30b7\u30e5\u30dc\u30fc\u30c9",
  searchPlaceholder: "\u30c1\u30e3\u30f3\u30cd\u30eb\u3092\u691c\u7d22",
  searchLabel: "\u691c\u7d22",
};

export default function AppLayout({ children }: AppLayoutProps) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-dashboard-surface text-gray-900">
      <header className="sticky top-0 z-30 border-b border-gray-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-4 sm:px-6">
          <div className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-youtube-red text-base font-semibold text-white">
              YA
            </span>
            <div>
              <p className="text-sm font-semibold tracking-tight text-gray-900">
                YouTube Analytics
              </p>
              <p className="text-xs text-gray-500">{copy.dashboard}</p>
            </div>
          </div>
          <div className="hidden flex-1 items-center md:flex">
            <div className="relative w-full">
              <input
                type="text"
                placeholder={copy.searchPlaceholder}
                className="w-full rounded-full border border-gray-200 bg-gray-50 px-4 py-2 text-sm text-gray-700 placeholder:text-gray-400 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
              />
              <span className="pointer-events-none absolute inset-y-0 right-4 flex items-center text-xs text-gray-400">
                {copy.searchLabel}
              </span>
            </div>
          </div>
          <div className="ml-auto flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 text-sm font-semibold text-gray-600">
            Z
          </div>
        </div>
      </header>

      <div className="mx-auto flex max-w-6xl gap-6 px-4 py-8 sm:px-6">
        <aside className="hidden w-56 shrink-0 flex-col gap-1 text-sm text-gray-600 lg:flex">
          {navItems.map((item) => {
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center rounded-r-full px-4 py-2 transition ${
                  isActive
                    ? "border-l-4 border-youtube-red bg-white font-semibold text-gray-900 shadow-sm"
                    : "border-l-4 border-transparent hover:bg-white"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </aside>

        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}
