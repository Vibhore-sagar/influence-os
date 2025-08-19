export const metadata = { title: "Influence OS", description: "Local MVP" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "sans-serif" }}>
        <nav style={{ padding: 12, borderBottom: "1px solid #ccc" }}>
          <a href="/">Home</a> | <a href="/onboarding">Onboarding</a> | <a href="/composer">Composer</a> | <a href="/analytics">Analytics</a>
        </nav>
        <a href="/auth/linkedin">LinkedIn</a>

        <main style={{ padding: 16 }}>{children}</main>
      </body>
    </html>
  );
}
