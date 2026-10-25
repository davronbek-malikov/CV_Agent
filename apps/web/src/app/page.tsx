"use client";

import { LangProvider } from "@/lib/lang-context";
import Header from "@/components/Header";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import HowItWorks from "@/components/HowItWorks";
import Comparison from "@/components/Comparison";
import Architecture from "@/components/Architecture";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <LangProvider>
      <Header />
      <main>
        <Hero />
        <Features />
        <HowItWorks />
        <Comparison />
        <Architecture />
      </main>
      <Footer />
    </LangProvider>
  );
}
