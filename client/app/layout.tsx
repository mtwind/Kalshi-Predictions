// client/app/layout.tsx
import { AppRouterCacheProvider } from "@mui/material-nextjs/v15-appRouter"; // Works for v16 too usually
import CssBaseline from "@mui/material/CssBaseline";
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Data Aggregation Dashboard",
  description: "Kalshi, Trends, YouTube, Wiki, TMDB, News",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AppRouterCacheProvider>
          {/* ThemeProvider would use a custom theme.ts file you create */}
          <CssBaseline />
          {children}
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
