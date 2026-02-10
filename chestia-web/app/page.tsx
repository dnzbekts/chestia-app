'use client'

import { useState } from 'react'
import { ChefHat, Zap, Sparkles, Search } from 'lucide-react'
import Link from 'next/link'
import Image from 'next/image'
import Hero from '@/components/hero'
import HowItWorks from '@/components/how-it-works'
import LanguageToggle from '@/components/language-toggle'
import Footer from '@/components/footer'
import { translations } from '@/lib/translations'

export default function Home() {
  const [language, setLanguage] = useState<'en' | 'tr'>('en')
  const t = translations[language]

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-md border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Image src="/chestia-logo.png" alt="Chestia Logo" width={152} height={50} />
          </div>
          <LanguageToggle language={language} setLanguage={setLanguage} />
        </div>
      </nav>

      {/* Hero Section */}
      <Hero language={language} t={t} />

      {/* How It Works Section */}
      <HowItWorks language={language} t={t} />

      {/* Recipe Preview Section */}
      <section className="py-20 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#ff6b5b]/5 to-transparent pointer-events-none"></div>
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-balance">
              {t.recipePreview.title}
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              {t.recipePreview.subtitle}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Recipe Card 1 */}
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-br from-[#ff6b5b]/20 to-transparent rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-500"></div>
              <div className="relative bg-card border border-border rounded-2xl overflow-hidden hover:border-primary transition-colors">
                <div className="h-48 bg-gradient-to-br from-[#ff6b5b] via-[#ff8c42] to-[#ffa500] relative overflow-hidden">
                  <Image
                    src="/recipe-example-1.jpg"
                    alt="Creamy garlic pasta"
                    fill
                    className="object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-2">{t.recipeExamples.pasta}</h3>
                  <p className="text-muted-foreground text-sm mb-4">
                    {t.recipeExamples.pastaDesc}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-3 py-1 rounded-full bg-secondary text-xs text-muted-foreground">20 min</span>
                    <span className="px-3 py-1 rounded-full bg-secondary text-xs text-muted-foreground">Easy</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Recipe Card 2 */}
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-br from-[#ff6b5b]/20 to-transparent rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-500"></div>
              <div className="relative bg-card border border-border rounded-2xl overflow-hidden hover:border-primary transition-colors">
                <div className="h-48 bg-gradient-to-br from-[#ffa500] via-[#ff8c42] to-[#ff6b5b] relative overflow-hidden">
                  <Image
                    src="/recipe-example-2.jpg"
                    alt="Quick stir fry"
                    fill
                    className="object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-2">{t.recipeExamples.stir}</h3>
                  <p className="text-muted-foreground text-sm mb-4">
                    {t.recipeExamples.stirDesc}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-3 py-1 rounded-full bg-secondary text-xs text-muted-foreground">15 min</span>
                    <span className="px-3 py-1 rounded-full bg-secondary text-xs text-muted-foreground">Easy</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Recipe Card 3 */}
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-br from-[#ff6b5b]/20 to-transparent rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-500"></div>
              <div className="relative bg-card border border-border rounded-2xl overflow-hidden hover:border-primary transition-colors">
                <div className="h-48 bg-gradient-to-br from-[#ff8c42] via-[#ffa500] to-[#ffb84d] relative overflow-hidden">
                  <Image
                    src="/recipe-example-3.jpg"
                    alt="Rustic vegetable soup"
                    fill
                    className="object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-2">{t.recipeExamples.soup}</h3>
                  <p className="text-muted-foreground text-sm mb-4">
                    {t.recipeExamples.soupDesc}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-3 py-1 rounded-full bg-secondary text-xs text-muted-foreground">30 min</span>
                    <span className="px-3 py-1 rounded-full bg-secondary text-xs text-muted-foreground">Medium</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              {t.features.title}
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-8 rounded-2xl border border-border hover:border-primary transition-colors group">
              <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-[#ff6b5b] to-[#ff8c42] flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2">{t.features.fast}</h3>
              <p className="text-muted-foreground">{t.features.fastDesc}</p>
            </div>

            <div className="p-8 rounded-2xl border border-border hover:border-primary transition-colors group">
              <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-[#ff8c42] to-[#ffa500] flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2">{t.features.creative}</h3>
              <p className="text-muted-foreground">{t.features.creativeDesc}</p>
            </div>

            <div className="p-8 rounded-2xl border border-border hover:border-primary transition-colors group">
              <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-[#ffa500] to-[#ffb84d] flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Search className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2">{t.features.smart}</h3>
              <p className="text-muted-foreground">{t.features.smartDesc}</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-[#ff6b5b]/10 via-transparent to-[#ff8c42]/10"></div>
        <div className="max-w-3xl mx-auto text-center relative z-10">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            {t.cta.title}
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            {t.cta.subtitle}
          </p>
          <Link href="/generate" className="inline-block px-8 py-4 rounded-full bg-gradient-to-r from-[#ff6b5b] to-[#ff8c42] text-white font-semibold hover:shadow-lg hover:shadow-[#ff6b5b]/50 transition-all duration-300 transform hover:scale-105">
            {t.cta.button}
          </Link>
        </div>
      </section>

      {/* Footer */}
      <Footer language={language} t={t} />
    </div>
  )
}
