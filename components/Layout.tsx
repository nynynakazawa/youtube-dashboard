"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";

type AppLayoutProps = {
  children: ReactNode;
};

const navItems = [
  { label: "\u30c0\u30c3\u30b7\u30e5\u30dc\u30fc\u30c9", href: "/" },
  { label: "\u30c1\u30e3\u30f3\u30cd\u30eb\u767b\u9332", href: "/channels/import" },
  { label: "\u30c1\u30e3\u30f3\u30cd\u30eb\u4e00\u89a7", href: "/channels" },
  { label: "\u30a2\u30ca\u30ea\u30c6\u30a3\u30af\u30b9", href: "/channels/demo" },
  { label: "\u52d5\u753b\u4e00\u89a7", href: "/channels/demo/videos" },
];

const copy = {
  dashboard: "\u30c0\u30c3\u30b7\u30e5\u30dc\u30fc\u30c9",
  searchPlaceholder: "\u30c1\u30e3\u30f3\u30cd\u30eb\u3092\u691c\u7d22",
  searchLabel: "\u691c\u7d22",
};

export default function AppLayout({ children }: AppLayoutProps) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen text-gray-900 relative z-10">
      <div className="mx-auto max-w-7xl px-8 py-8 pb-8 sm:py-12 sm:px-12 lg:px-16 relative z-10">
        <main className="w-full">{children}</main>
      </div>
    </div>
  );
}
