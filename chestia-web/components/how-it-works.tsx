'use client'

import React from "react"

import { Search, Zap, ChefHat } from 'lucide-react'
import type { Translation } from '@/lib/translations'

interface HowItWorksProps {
  language: 'en' | 'tr'
  t: Translation
}

export default function HowItWorks({ t }: HowItWorksProps) {
  return (
    <section className="py-20 px-4 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-[#ff6b5b]/5 via-transparent to-[#ff8c42]/5 pointer-events-none"></div>

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            {t.howItWorks.title}
          </h2>
          <p className="text-lg text-muted-foreground">
            {t.howItWorks.subtitle}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {/* Connecting Lines */}
          <div className="hidden md:block absolute top-1/4 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[#ff6b5b]/20 to-transparent"></div>

          {/* Step 1 */}
          <StepCard
            icon={<Search className="w-6 h-6 text-white" />}
            number="01"
            title={t.howItWorks.step1.title}
            description={t.howItWorks.step1.description}
            gradient="from-[#ff6b5b] to-[#ff8c42]"
          />

          {/* Step 2 */}
          <StepCard
            icon={<Zap className="w-6 h-6 text-white" />}
            number="02"
            title={t.howItWorks.step2.title}
            description={t.howItWorks.step2.description}
            gradient="from-[#ff8c42] to-[#ffa500]"
            highlighted
          />

          {/* Step 3 */}
          <StepCard
            icon={<ChefHat className="w-6 h-6 text-white" />}
            number="03"
            title={t.howItWorks.step3.title}
            description={t.howItWorks.step3.description}
            gradient="from-[#ffa500] to-[#ffb84d]"
          />
        </div>
      </div>
    </section>
  )
}

interface StepCardProps {
  icon: React.ReactNode
  number: string
  title: string
  description: string
  gradient: string
  highlighted?: boolean
}

function StepCard({ icon, number, title, description, gradient, highlighted }: StepCardProps) {
  return (
    <div className={`relative group ${highlighted ? 'md:-translate-y-4' : ''}`}>
      {/* Glow Background */}
      <div className={`absolute inset-0 bg-gradient-to-br ${gradient} rounded-2xl blur-xl opacity-20 group-hover:opacity-30 transition-opacity duration-300`}></div>

      {/* Card */}
      <div className={`relative bg-card border ${highlighted ? 'border-primary' : 'border-border'} rounded-2xl p-8 hover:border-primary transition-colors duration-300 h-full`}>
        {/* Number Badge */}
        <div className={`inline-flex items-center justify-center w-14 h-14 rounded-lg bg-gradient-to-br ${gradient} mb-6`}>
          <span className="text-2xl font-bold text-white">{number}</span>
        </div>

        {/* Icon */}
        <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg bg-gradient-to-br ${gradient} mb-6 ml-4`}>
          {icon}
        </div>

        {/* Content */}
        <h3 className="text-2xl font-bold mb-4">{title}</h3>
        <p className="text-muted-foreground leading-relaxed">{description}</p>

        {/* Arrow */}
        <div className="mt-8 flex items-center text-primary opacity-0 group-hover:opacity-100 transform -translate-x-2 group-hover:translate-x-0 transition-all duration-300">
          <span className="text-sm font-semibold">Learn more</span>
          <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </div>
  )
}
