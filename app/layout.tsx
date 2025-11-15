import type { Metadata } from "next";
import { Inter, Roboto_Mono } from "next/font/google";
import AppLayout from "@/components/Layout";
import "./globals.css";

const inter = Inter({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const robotoMono = Roboto_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "YouTube \u30c1\u30e3\u30f3\u30cd\u30eb\u89e3\u6790\u30c0\u30c3\u30b7\u30e5\u30dc\u30fc\u30c9",
  description:
    "YouTube \u30c1\u30e3\u30f3\u30cd\u30eb\u306e\u6210\u9577\u3084\u52d5\u753b\u30d1\u30d5\u30a9\u30fc\u30de\u30f3\u30b9\u3092\u4fef\u77b0\u3067\u304d\u308b\u7ba1\u7406\u30c0\u30c3\u30b7\u30e5\u30dc\u30fc\u30c9\u3067\u3059\u3002",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body className={`${inter.variable} ${robotoMono.variable} antialiased`}>
        <AppLayout>{children}</AppLayout>
      </body>
    </html>
  );
}
