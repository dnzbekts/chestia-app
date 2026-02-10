'use client'

import React, { useState, useEffect } from 'react'
import Image from 'next/image'
import { CopilotChat } from "@copilotkit/react-ui"
import { useCoAgent } from "@copilotkit/react-core"
import LanguageToggle from '@/components/language-toggle'
import Footer from '@/components/footer'
import { translations } from '@/lib/translations'

// Define the Agent State matches the backend GraphState
interface AgentState {
    ingredients: string[];
    original_ingredients: string[];
    difficulty: string;
    lang: string;
    error: string;
}

export default function GeneratePage() {
    const [language, setLanguage] = useState<'en' | 'tr'>('en')
    const t = translations[language]

    // Sync language state with the backend agent
    const { state, setState } = useCoAgent<AgentState>({
        name: "chestia_recipe_agent",
        initialState: {
            ingredients: [],
            difficulty: "",
            lang: "en",
        }
    });

    // Update agent state when language changes
    useEffect(() => {
        if (state && state.lang !== language) {
            setState({ ...state, lang: language })
        }
    }, [language, setState, state])

    return (
        <div className="relative min-h-screen w-full overflow-hidden bg-background text-foreground flex flex-col">

            {/* Navigation (Sticky Header) */}
            <nav className="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-md border-b border-border">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        {/* Link back to home via logo */}
                        <a href="/" className="flex items-center">
                            <Image src="/chestia-logo.png" alt="Chestia Logo" width={152} height={50} priority />
                        </a>
                    </div>
                    <LanguageToggle language={language} setLanguage={setLanguage} />
                </div>
            </nav>

            {/* Blurred Background Grid (Fixed) */}
            <div className="fixed inset-0 grid grid-cols-2 grid-rows-2 gap-0 z-0 opacity-40 pointer-events-none">
                <div className="relative w-full h-full">
                    <Image src="/recipe-example-1.jpg" alt="Background Food" fill className="object-cover blur-[8px]" />
                </div>
                <div className="relative w-full h-full">
                    <Image src="/recipe-example-2.jpg" alt="Background Food" fill className="object-cover blur-[8px]" />
                </div>
                <div className="relative w-full h-full">
                    <Image src="/recipe-example-3.jpg" alt="Background Food" fill className="object-cover blur-[8px]" />
                </div>
                <div className="relative w-full h-full">
                    <Image src="/hero-food.jpg" alt="Background Food" fill className="object-cover blur-[8px]" />
                </div>
                {/* Overlay Gradient */}
                <div className="absolute inset-0 bg-black/60"></div>
            </div>


            {/* Main Content Area */}
            <main className="flex-grow relative z-10 flex items-center justify-center pt-24 pb-12 px-4">
                <div className="w-full max-w-2xl">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center p-3 rounded-full">
                            <Image src="/chestia-logo-c.png" alt="Chestia Logo" width={30} height={30} priority />
                        </div>
                        <p className="text-white/70">{language === 'en' ? 'Your Intelligent Culinary Assistant' : 'Yapay Zeka Aşçınız'}</p>
                    </div>

                    {/* Chat Container */}
                    <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden h-[600px] flex flex-col ring-1 ring-white/5">
                        <CopilotChat
                            className="flex-1 w-full h-full [&_.copilotKitChat]:bg-transparent [&_.copilotKitInput]:bg-white/5 [&_.copilotKitInput]:border-white/10"
                            instructions={`You are Chef Chestia, a warm and knowledgeable culinary expert helping users create delicious recipes.

CONVERSATION FLOW:
1. Warmly greet and ask for ingredients (minimum 3 required)
2. Once ingredients given, ask for difficulty level (easy, intermediate, hard)
3. Confirm choices, then generate the recipe

RULES:
- ALWAYS collect BOTH ingredients AND difficulty before proceeding
- If fewer than 3 ingredients, politely request more
- Be concise, friendly, and encouraging
- Current language: ${language === 'en' ? 'English' : 'Turkish'}`}
                            labels={{
                                title: "Chestia",
                                initial: language === 'en' ? "Hi! What ingredients do you have today?" : "Merhaba! Bugün hangi malzemeleriniz var?",
                                placeholder: language === 'en' ? "Type ingredients (e.g., Chicken, Rice)..." : "Malzemeleri yazın (örn. Tavuk, Pirinç)..."
                            }}
                        />
                    </div>
                </div>
            </main>

            {/* Footer */}
            <div className="relative z-10">
                <Footer language={language} t={t} />
            </div>
        </div>
    )
}
