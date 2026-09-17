import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LeadHunter AI",
  description: "AI-powered lead generation and outreach platform"
};

export default function RootLayout({
  children
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}