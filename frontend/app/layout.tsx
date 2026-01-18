import './globals.css'

export const metadata = {
  title: 'Invoice Extraction App',
  description: 'Extract and manage invoice data using AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
