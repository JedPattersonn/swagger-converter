import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Swagger Converter",
  description:
    "Convert Swagger 2.0 to OpenAPI 3.0 format for free with this simple online tool. No registration required. We also have a public API that you can use to integrate this into your CI/CD pipeline.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
