export const translations = {
  en: {
    nav: {
      home: 'Home',
      about: 'About',
      contact: 'Contact',
      faq: 'FAQ',
    },
    hero: {
      title: "Unlock Your Kitchen's Potential",
      subtitle: 'Chestia turns your leftover ingredients into Michelin-star ideas. Stop wasting, start creating.',
      cta: 'Generate Recipe',
      inputPlaceholder: 'Tell us what you have...',
    },
    howItWorks: {
      title: 'How It Works',
      subtitle: 'Three simple steps to delicious recipes',
      step1: {
        title: 'Tell Us What You Have',
        description: 'Input the ingredients currently in your fridge or pantry. No detail is too small.',
      },
      step2: {
        title: 'The Magic Happens',
        description: 'Our AI analyzes flavor profiles to construct the perfect meal from your available stocks.',
      },
      step3: {
        title: 'Cook & Impress',
        description: 'Follow step-by-step instructions to create a dish that looks and tastes professional.',
      },
    },
    recipePreview: {
      title: 'Inspiring Recipes from Simple Ingredients',
      subtitle: 'Every recipe is crafted to maximize flavor while minimizing waste. From breakfast to dinner.',
    },
    recipeExamples: {
      pasta: 'Creamy Garlic Pasta',
      pastaDesc: 'Transform simple pasta and pantry staples into a restaurant-quality cream sauce.',
      stir: 'Quick Stir Fry',
      stirDesc: 'Combine fresh vegetables with your choice of protein for a quick weeknight dinner.',
      soup: 'Rustic Vegetable Soup',
      soupDesc: 'A hearty, warming soup that makes the most of seasonal produce.',
    },
    features: {
      title: 'Why Choose Chestia',
      fast: 'Lightning Fast',
      fastDesc: 'Get recipe suggestions in seconds. No endless scrolling through complicated cookbooks.',
      creative: 'Creative Combinations',
      creativeDesc: 'Discover flavor pairings you never thought possible. Elevate your cooking skills.',
      smart: 'Smart Suggestions',
      smartDesc: 'AI-powered recipes that understand ingredient compatibility and dietary preferences.',
    },
    cta: {
      title: 'Ready to Cook Something Amazing?',
      subtitle: 'Start exploring recipes from your ingredients today. Free to use, always.',
      button: 'Generate Your First Recipe',
    },
    footer: {
      about: 'About Us',
      aboutDesc: 'Chestia was born from a simple question: Why is cooking dinner so hard even when the fridge is full?',
      contact: 'Get in Touch',
      email: 'hello@chestia.web',
      address: '123 Culinary Ave, Tech District',
      links: 'Quick Links',
      faq: 'FAQ',
      privacy: 'Privacy Policy',
      terms: 'Terms of Service',
      copyright: '© 2026 Chestia. All rights reserved.',
    },
  },
  tr: {
    nav: {
      home: 'Ana Sayfa',
      about: 'Hakkında',
      contact: 'İletişim',
      faq: 'SSS',
    },
    hero: {
      title: 'Mutfağınızın Potansiyelini Ortaya Çıkarın',
      subtitle: 'Chestia, elinizde kalan malzemeleri Michelin yıldızlı fikirlere dönüştürür. Daha fazla harcamayın, yaratmaya başlayın.',
      cta: 'Tarif Oluştur',
      inputPlaceholder: 'Ne malzemeniz var söyleyin...',
    },
    howItWorks: {
      title: 'Nasıl Çalışır',
      subtitle: 'Lezzetli tariflere ulaşmak için üç basit adım',
      step1: {
        title: 'Elindekini Bize Söyle',
        description: 'Buzdolabında veya pantiyonda olan malzemeleri gir. Hiçbir detay çok küçük değildir.',
      },
      step2: {
        title: 'Büyü Gerçekleşir',
        description: 'AI yapay zekamız lezzet profillerini analiz ederek mükemmel yemeği oluşturur.',
      },
      step3: {
        title: 'Pişir ve Etkilendiri',
        description: 'Adım adım talimatları izleyerek profesyonel görünümlü bir yemek yarat.',
      },
    },
    recipePreview: {
      title: 'Basit Malzemelerden İlham Veren Tarifler',
      subtitle: 'Her tarif, lezzeti en yüksek seviyeye çıkarırken atıkları en aza indirmek için tasarlanmıştır.',
    },
    recipeExamples: {
      pasta: 'Krem Sarımsaklı Makarna',
      pastaDesc: 'Basit makarnayı restoran kalitesinde bir krem sosuna dönüştür.',
      stir: 'Hızlı Tavada Pişme',
      stirDesc: 'Taze sebzeleri tercih ettiğin proteini ile birleştirerek hızlı bir akşam yemeği hazırla.',
      soup: 'Rustic Sebze Çorbası',
      soupDesc: 'Sezonluk ürünleri en iyi şekilde kullanan sıcak ve doyurucu bir çorba.',
    },
    features: {
      title: 'Neden Chestia?',
      fast: 'Işık Hızında',
      fastDesc: 'Saniyeler içinde tarif önerileri al. Karışık mutfak kitaplarında sonsuz kaydırma yok.',
      creative: 'Yaratıcı Kombinasyonlar',
      creativeDesc: 'Asla düşünmediğin lezzet kombinasyonlarını keşfet. Mutfak becerilerini geliştir.',
      smart: 'Akıllı Öneriler',
      smartDesc: 'Malzeme uyumluluğunu ve diyet tercihlerini anlayan yapay zeka destekli tarifler.',
    },
    cta: {
      title: 'Harika Bir Şey Pişirmeye Hazır Mısın?',
      subtitle: 'Bugün malzemelerinizden tarifler keşfetmeye başlayın. Ücretsiz ve her zaman.',
      button: 'İlk Tarifinizi Oluşturun',
    },
    footer: {
      about: 'Hakkımızda',
      aboutDesc: 'Chestia, basit bir sorudan doğdu: Buzdolabı doluyken neden akşam yemeği pişirmek bu kadar zor?',
      contact: 'İletişim',
      email: 'hello@chestia.web',
      address: '123 Aşçılık Cad., Teknoloji Bölgesi',
      links: 'Hızlı Bağlantılar',
      faq: 'SSS',
      privacy: 'Gizlilik Politikası',
      terms: 'Hizmet Şartları',
      copyright: '© 2026 Chestia. Tüm hakları saklıdır.',
    },
  },
} as const

export type Translation = typeof translations[keyof typeof translations]
