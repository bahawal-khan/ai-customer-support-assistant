import { Navbar } from "@/components/shell/navbar";
import { Sidebar } from "@/components/shell/sidebar";
import { Footer } from "@/components/shell/footer";
import { PageTransition } from "@/components/shell/page-transition";

export default function ShellLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <div className="content-container flex flex-1 items-start">
        <Sidebar />
        <main className="min-w-0 flex-1 py-6 lg:pl-6">
          <PageTransition>{children}</PageTransition>
        </main>
      </div>
      <Footer />
    </div>
  );
}
