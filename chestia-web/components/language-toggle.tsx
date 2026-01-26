'use client'

import { Globe } from 'lucide-react'

interface LanguageToggleProps {
  language: 'en' | 'tr'
  setLanguage: (lang: 'en' | 'tr') => void
}

export default function LanguageToggle({ language, setLanguage }: LanguageToggleProps) {
  return (
    <div className="flex items-center gap-1 bg-secondary rounded-lg p-1">
      <button
        onClick={() => setLanguage('en')}
        className={`px-4 py-2 rounded-md transition-all font-semibold flex items-center gap-2 ${
          language === 'en'
            ? 'bg-primary text-primary-foreground'
            : 'text-muted-foreground hover:text-foreground'
        }`}
      >
        <Globe className="w-4 h-4" />
        EN
      </button>
      <button
        onClick={() => setLanguage('tr')}
        className={`px-4 py-2 rounded-md transition-all font-semibold ${
          language === 'tr'
            ? 'bg-primary text-primary-foreground'
            : 'text-muted-foreground hover:text-foreground'
        }`}
      >
        TR
      </button>
    </div>
  )
}
