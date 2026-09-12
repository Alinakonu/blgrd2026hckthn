import type { Metadata } from "next";
import { Syne, Figtree } from "next/font/google";
import "./globals.css";

const display = Syne({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["600", "700", "800"],
});

const sans = Figtree({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "SoilShift — climate-aware soil adaptation",
  description:
    "Pin a field, pick a crop, get a ranked soil-adaptation checklist for the 2030s and 2050s.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${display.variable} ${sans.variable} antialiased`}>
        <div className="atmosphere" aria-hidden />
        {children}
      </body>
    </html>
  );
}
