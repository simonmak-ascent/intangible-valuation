import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";

// No SessionProvider. There is no session: auth and every account surface were removed on
// 2026-11-19, so a client provider that fetched `/v1/auth/session` on mount was making a request that
// could only fail, and every page rendering this shell logged the failure.
export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Header />
      <main className="flex-1">{children}</main>
      <Footer />
    </>
  );
}
