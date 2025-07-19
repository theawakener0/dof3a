import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/navbar";
export const metadata: Metadata = {
  title: "DOF3A",
  description: "",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <nav className="mb-10">
          <Navbar />
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}
