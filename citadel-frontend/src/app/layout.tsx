
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { CopilotKit } from "@copilotkit/react-core";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Project Citadel",
  description: "AI Agent Framework with CopilotKit Integration",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <CopilotKit
          apiUrl={process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
          runtimeUrl="http://localhost:8000"
          publicApiKey="dummy-key"
        >
          {children}
        </CopilotKit>
      </body>
    </html>
  );
}
