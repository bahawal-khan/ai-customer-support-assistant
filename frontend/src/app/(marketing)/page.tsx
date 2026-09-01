import type { Metadata } from "next";

import { Faq } from "@/components/marketing/faq";
import { Features } from "@/components/marketing/features";
import { Hero } from "@/components/marketing/hero";
import { HowItWorks } from "@/components/marketing/how-it-works";
import { ProductShowcase } from "@/components/marketing/product-showcase";
import { WhyUseIt } from "@/components/marketing/why-use-it";

export const metadata: Metadata = {
  title: "AI Customer Support Assistant",
  description:
    "AI-powered customer complaint analysis, grounded support knowledge retrieval, and response assistance.",
};

export default function LandingPage() {
  return (
    <>
      <Hero />
      <Features />
      <HowItWorks />
      <ProductShowcase />
      <WhyUseIt />
      <Faq />
    </>
  );
}
