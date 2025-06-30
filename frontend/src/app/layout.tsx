/**
 * Root layout for Smart CRM SaaS application.
 * This layout wraps the entire application and provides global providers,
 * fonts, and metadata configuration.
 */

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/auth-context";

// Load custom fonts
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Application metadata
export const metadata: Metadata = {
  title: "Smart CRM SaaS - Customer Relationship Management",
  description: "A comprehensive CRM solution for managing clients, projects, payments, and expenses.",
  keywords: ["CRM", "Customer Management", "Project Management", "SaaS"],
  authors: [{ name: "Smart CRM Team" }],
  viewport: "width=device-width, initial-scale=1",
};

// Root layout component props
interface RootLayoutProps {
  children: React.ReactNode;
}

/**
 * Root layout component that wraps the entire application.
 * Provides global providers, fonts, and base HTML structure.
 */
export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        suppressHydrationWarning
      >
        {/* Authentication Provider wraps the entire app */}
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
