'use client'

import React from "react"

import { useState } from 'react'
import { Search, ArrowRight } from 'lucide-react'
import Image from 'next/image'
import type { Translation } from '@/lib/translations'

interface HeroProps {
  language: 'en' | 'tr'
  t: Translation
}

export default function Hero({ t }: HeroProps) {
  const [input, setInput] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implement recipe generation
  }

  return (
    <section className="pt-32 pb-20 px-4 relative overflow-hidden min-h-[90vh] flex items-center">
      {/* Background Image with Overlay */}
      <div className="absolute inset-0 z-0">
        <Image
          src="/hero-food.jpg"
          alt="Fresh ingredients"
          fill
          className="object-cover object-center opacity-20"
          priority
          quality={85}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/50 to-background"></div>
      </div>

      {/* Background elements */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-[#ff6b5b]/20 to-transparent rounded-full blur-3xl"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-gradient-to-tr from-[#ff8c42]/20 to-transparent rounded-full blur-3xl"></div>

      <div className="max-w-4xl mx-auto text-center relative z-10">

        {/* Main Headline */}
        <h1 className="text-5xl md:text-7xl font-bold mb-6 text-balance leading-tight">
          {t.hero.title}
        </h1>

        {/* Subheadline */}
        <p className="text-xl md:text-2xl text-muted-foreground mb-10 text-balance max-w-2xl mx-auto leading-relaxed">
          {t.hero.subtitle}
        </p>

        {/* Input Section */}
        <form onSubmit={handleSubmit} className="mb-12">
          <div className="relative max-w-2xl mx-auto">
            <div className="absolute inset-0 bg-gradient-to-r from-[#ff6b5b]/30 to-[#ff8c42]/30 rounded-2xl blur-xl"></div>
            <div className="relative flex items-center bg-card border border-border rounded-2xl overflow-hidden hover:border-primary transition-colors">
              <Search className="w-6 h-6 ml-5 text-muted-foreground" />
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={t.hero.inputPlaceholder}
                className="flex-1 px-4 py-4 bg-transparent outline-none text-foreground placeholder-muted-foreground"
              />
              <button
                type="submit"
                className="mr-2 px-6 py-2 rounded-lg bg-gradient-to-r from-[#ff6b5b] to-[#ff8c42] text-white font-semibold hover:shadow-lg hover:shadow-[#ff6b5b]/50 transition-all duration-300 flex items-center gap-2"
              >
                {t.hero.cta}
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </form>

        {/* Suggestion Chips */}
        <div className="flex flex-wrap justify-center gap-3">
          <SuggestionChip text="Tomato, Garlic, Olive Oil" />
          <SuggestionChip text="Chicken, Rice, Soy Sauce" />
          <SuggestionChip text="Pasta, Milk, Cheese" />
        </div>
      </div>
    </section>
  )
}

function Sparkle({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="currentColor"
      viewBox="0 0 20 20"
    >
      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
    </svg>
  )
}

function SuggestionChip({ text }: { text: string }) {
  return (
    <button className="px-4 py-2 rounded-full border border-border bg-secondary hover:bg-card hover:border-primary transition-all text-sm text-muted-foreground hover:text-foreground group">
      {text}
      <span className="ml-2 inline-block group-hover:translate-x-1 transition-transform">→</span>
    </button>
  )
}
