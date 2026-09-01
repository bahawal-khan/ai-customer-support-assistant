"use client";

import * as React from "react";
import { motion } from "motion/react";
import { Bot, Mail } from "lucide-react";

import { GithubIcon, LinkedinIcon } from "@/components/icons/brand-icons";
import { useMktMotion } from "@/components/marketing/mkt-motion";

const NAV_LINKS = [
  { href: "#hero", label: "Home" },
  { href: "#how-it-works", label: "How It Works" },
  { href: "#features", label: "Features & Capabilities" },
  { href: "#product-showcase", label: "Product Showcase" },
  { href: "#why-use-it", label: "Why Use It" },
  { href: "#faq", label: "FAQ" },
];

const CONTACT_LINKS = [
  { href: "https://github.com/bahawal-khan", label: "GitHub", icon: GithubIcon },
  {
    href: "https://www.linkedin.com/in/bahawal-khan-9b1124313/",
    label: "LinkedIn",
    icon: LinkedinIcon,
  },
  { href: "mailto:khanbahawal2004@gmail.com", label: "Email", icon: Mail },
];

export function MktFooter() {
  const { item } = useMktMotion();
  const year = new Date().getFullYear();

  return (
    <motion.footer
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.3 }}
      variants={item}
      className="mkt border-t border-[var(--mkt-text-muted)]/10 bg-[var(--mkt-bg)] pt-16 pb-8 text-[var(--mkt-text)] sm:pt-20"
    >
      <div className="content-container flex flex-col gap-10">
        <div className="flex flex-col gap-8 sm:flex-row sm:items-start sm:justify-between">
          <div className="max-w-xs">
            <a href="#hero" className="flex items-center gap-2 font-semibold tracking-tight">
              <span
                className="flex size-7 items-center justify-center rounded-lg text-white"
                style={{ background: "var(--mkt-violet)" }}
              >
                <Bot className="size-4" />
              </span>
              <span>AI Customer Support</span>
            </a>
            <p className="mt-3 text-sm leading-relaxed text-[var(--mkt-text-muted)]">
              AI-powered customer complaint analysis, grounded support knowledge retrieval, and
              response assistance.
            </p>
          </div>

          <nav aria-label="Section navigation" className="flex flex-col gap-2 text-sm sm:items-end">
            {NAV_LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-[var(--mkt-text-muted)] transition-colors duration-150 hover:text-[var(--mkt-text)] hover:underline hover:underline-offset-4"
              >
                {link.label}
              </a>
            ))}
          </nav>

          <div className="flex flex-col gap-3 sm:items-end">
            <p className="text-sm font-medium text-[var(--mkt-text)]">Bahawal Khan</p>
            <p className="-mt-2 text-xs text-[var(--mkt-text-muted)]">AI/ML &amp; Full Stack Developer</p>
            <div className="flex items-center gap-4">
              {CONTACT_LINKS.map((contact) => (
                <a
                  key={contact.label}
                  href={contact.href}
                  target={contact.href.startsWith("http") ? "_blank" : undefined}
                  rel={contact.href.startsWith("http") ? "noopener noreferrer" : undefined}
                  aria-label={contact.label}
                  className="text-[var(--mkt-text-muted)] transition-colors duration-150 hover:text-[var(--mkt-violet)]"
                >
                  <contact.icon className="size-4" />
                </a>
              ))}
            </div>
          </div>
        </div>

        <div className="border-t border-[var(--mkt-text-muted)]/10 pt-6 text-center text-xs text-[var(--mkt-text-muted)]">
          © {year} Bahawal Khan.
        </div>
      </div>
    </motion.footer>
  );
}
