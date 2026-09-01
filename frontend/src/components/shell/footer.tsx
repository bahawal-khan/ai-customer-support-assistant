import Link from "next/link";
import { Bot, Mail } from "lucide-react";
import { GithubIcon, LinkedinIcon } from "@/components/icons/brand-icons";

const PRODUCT_LINKS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/complaints/new", label: "New Complaint" },
  { href: "/history", label: "History" },
  { href: "/knowledge-base", label: "Knowledge Base" },
];

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-border/80 bg-background">
      <div className="content-container grid grid-cols-2 gap-8 py-10 sm:grid-cols-3">
        <div className="col-span-2 sm:col-span-1">
          <div className="flex items-center gap-2">
            <span className="flex size-7 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <Bot className="size-4" />
            </span>
            <p className="font-semibold tracking-tight">AI Customer Support Assistant</p>
          </div>
          <p className="mt-2 text-sm text-muted-foreground">
            AI-powered customer complaint analysis, grounded support knowledge retrieval, and
            response assistance.
          </p>
        </div>

        <div>
          <p className="text-sm font-medium text-foreground">Product</p>
          <ul className="mt-3 space-y-2">
            {PRODUCT_LINKS.map((link) => (
              <li key={link.href}>
                <Link href={link.href} className="text-sm text-muted-foreground hover:text-foreground">
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <p className="text-sm font-medium text-foreground">Developer</p>
          <p className="mt-3 text-sm text-muted-foreground">Bahawal Khan</p>
          <p className="text-sm text-muted-foreground">AI/ML &amp; Full Stack Developer</p>
          <div className="mt-3 flex items-center gap-3">
            <a
              href="https://github.com/bahawal-khan"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="GitHub"
              className="text-muted-foreground hover:text-foreground"
            >
              <GithubIcon className="size-4" />
            </a>
            <a
              href="https://www.linkedin.com/in/bahawal-khan-9b1124313/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="LinkedIn"
              className="text-muted-foreground hover:text-foreground"
            >
              <LinkedinIcon className="size-4" />
            </a>
            <a
              href="mailto:khanbahawal2004@gmail.com"
              aria-label="Email"
              className="text-muted-foreground hover:text-foreground"
            >
              <Mail className="size-4" />
            </a>
          </div>
        </div>
      </div>

      <div className="border-t border-border/80">
        <div className="content-container flex flex-col items-center justify-between gap-2 py-4 text-xs text-muted-foreground sm:flex-row">
          <p>© {year} AI Customer Support Assistant</p>
          <p>Crafted by Bahawal Khan</p>
        </div>
      </div>
    </footer>
  );
}
