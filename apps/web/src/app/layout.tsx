import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "../styles/globals.css";
import { Toaster } from "sonner";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AgroMind - Autonomous Agriculture Intelligence",
  description: "The AI-native operating system for post-chemical agriculture",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}): JSX.Element {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <div className="relative flex h-screen flex-col overflow-hidden bg-background">
          {children}
          <Toaster position="bottom-right" />
        </div>
      </body>
    </html>
  );
}
