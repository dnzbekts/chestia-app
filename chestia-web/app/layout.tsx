import React from "react"
import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import './globals.css'
import { CopilotKit } from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css";

const _geist = Geist({ subsets: ["latin"] });
const _geistMono = Geist_Mono({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: 'Chestia - Transform Your Ingredients Into Delicious Recipes',
  description: 'Chestia turns your leftover ingredients into creative recipes. Stop wasting, start creating amazing dishes with what you have.',
  generator: 'v0.app',
  keywords: 'recipe generator, ingredient-based cooking, food waste reduction, AI recipes',
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`font-sans antialiased bg-background text-foreground`}>
        <CopilotKit runtimeUrl="/api/copilotkit" agent="chestia_recipe_agent">
          {children}
        </CopilotKit>
        <Analytics />
      </body>
    </html>
  )
}
