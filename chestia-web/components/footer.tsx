'use client'

import { Mail, MapPin, Facebook, Twitter, Instagram } from 'lucide-react'
import type { Translation } from '@/lib/translations'

interface FooterProps {
  language: 'en' | 'tr'
  t: Translation
}

export default function Footer({ t }: FooterProps) {
  return (
    <footer className="bg-card border-t border-border">
      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          {/* About Section */}
          <div>
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-[#ff6b5b] to-[#ff8c42] flex items-center justify-center">
                <span className="text-xs text-white font-bold">C</span>
              </div>
              {t.footer.about}
            </h3>
            <p className="text-muted-foreground leading-relaxed text-sm">
              {t.footer.aboutDesc}
            </p>
          </div>

          {/* Contact Section */}
          <div>
            <h3 className="text-lg font-bold mb-4">{t.footer.contact}</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-sm text-muted-foreground hover:text-foreground transition-colors">
                <Mail className="w-4 h-4" />
                <a href={`mailto:${t.footer.email}`}>{t.footer.email}</a>
              </div>
              <div className="flex items-center gap-3 text-sm text-muted-foreground hover:text-foreground transition-colors">
                <MapPin className="w-4 h-4" />
                <span>{t.footer.address}</span>
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-bold mb-4">{t.footer.links}</h3>
            <nav className="space-y-2">
              <a href="#" className="block text-sm text-muted-foreground hover:text-foreground transition-colors">
                {t.footer.faq}
              </a>
              <a href="#" className="block text-sm text-muted-foreground hover:text-foreground transition-colors">
                {t.footer.privacy}
              </a>
              <a href="#" className="block text-sm text-muted-foreground hover:text-foreground transition-colors">
                {t.footer.terms}
              </a>
            </nav>
          </div>

          {/* Social Links */}
          <div>
            <h3 className="text-lg font-bold mb-4">Follow Us</h3>
            <div className="flex gap-4">
              <a
                href="#"
                className="w-10 h-10 rounded-lg bg-secondary hover:bg-primary hover:text-primary-foreground transition-colors flex items-center justify-center group"
                aria-label="Facebook"
              >
                <Facebook className="w-5 h-5" />
              </a>
              <a
                href="#"
                className="w-10 h-10 rounded-lg bg-secondary hover:bg-primary hover:text-primary-foreground transition-colors flex items-center justify-center group"
                aria-label="Twitter"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a
                href="#"
                className="w-10 h-10 rounded-lg bg-secondary hover:bg-primary hover:text-primary-foreground transition-colors flex items-center justify-center group"
                aria-label="Instagram"
              >
                <Instagram className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-border mb-8"></div>

        {/* Bottom Section */}
        <div className="flex flex-col md:flex-row justify-between items-center">
          <p className="text-sm text-muted-foreground">{t.footer.copyright}</p>
          <div className="text-xs text-muted-foreground mt-4 md:mt-0">
            Made with <span className="text-primary">♥</span> for food lovers
          </div>
        </div>
      </div>
    </footer>
  )
}
