import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Your Whole Personality",
  description: "A playful Qloo-powered cultural taste investigation.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
