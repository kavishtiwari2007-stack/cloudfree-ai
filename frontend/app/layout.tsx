import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CloudFreeAI - ISRO Remote Sensing Platform',
  description: 'AI-Powered Multi-Temporal Satellite Reconstruction & Disaster Intelligence',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
      </head>
      <body class="bg-[#0b0f19] text-[#e2e8f0] min-h-screen font-mono flex flex-col">
        {children}
      </body>
    </html>
  )
}
