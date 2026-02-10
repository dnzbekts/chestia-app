import React from 'react'
import { Clock, Users, ChefHat } from "lucide-react"

interface RecipeProps {
    recipe: {
        name: string;
        ingredients: string[];
        steps: string[];
        metadata?: {
            [key: string]: any;
        };
    }
}

export default function RecipeCard({ recipe }: RecipeProps) {
    if (!recipe) return null;

    // Helper to decode HTML entities
    const decodeHtml = (html: string) => {
        const txt = document.createElement("textarea");
        txt.innerHTML = html;
        return txt.value;
    };

    // Helper to safely decode string
    const safeDecode = (str: string) => {
        if (typeof window === 'undefined') {
            return str
                .replace(/&#39;/g, "'")
                .replace(/&quot;/g, '"')
                .replace(/&amp;/g, '&')
                .replace(/&lt;/g, '<')
                .replace(/&gt;/g, '>');
        }
        try {
            return decodeHtml(str);
        } catch (e) {
            return str;
        }
    }

    // Robust list parser
    const parseList = (input: any): string[] => {
        if (Array.isArray(input)) {
            return input.map(s => safeDecode(String(s)));
        }

        if (typeof input === 'string') {
            let parsed: string[] = [];
            try {
                // Try JSON parse
                const json = JSON.parse(input);
                if (Array.isArray(json)) {
                    parsed = json;
                } else {
                    throw new Error("Not array");
                }
            } catch (e) {
                // Try Python-style list string
                if (input.trim().startsWith('[') && input.trim().endsWith(']')) {
                    try {
                        const fixed = input.replace(/'/g, '"');
                        const json = JSON.parse(fixed);
                        if (Array.isArray(json)) parsed = json;
                        else parsed = [input];
                    } catch (err) {
                        parsed = [input];
                    }
                } else {
                    // Split by newline if present
                    if (input.includes('\n')) {
                        parsed = input.split('\n').filter((s: string) => s.trim().length > 0);
                    } else {
                        // Fallback to single item (avoid comma split as it breaks sentences)
                        parsed = [input];
                    }
                }
            }
            return parsed.map(s => safeDecode(String(s)));
        }

        return [];
    }

    const steps = parseList(recipe.steps);
    const ingredients = parseList(recipe.ingredients);

    return (
        <div className="w-full max-w-2xl mt-8 bg-black/40 backdrop-blur-xl border border-white/10 text-white shadow-2xl overflow-hidden rounded-xl ring-1 ring-white/5 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="border-b border-white/10 p-6 pb-6">
                <div className="flex justify-between items-start gap-4">
                    <div>
                        <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-primary/10 text-primary hover:bg-primary/20 mb-2">
                            <ChefHat className="w-3 h-3 mr-1" />
                            Generated Recipe
                        </div>
                        <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/70">
                            {recipe.name}
                        </h2>
                    </div>
                </div>
            </div>

            <div className="p-6 pt-6 space-y-8">
                {/* Ingredients Section */}
                <div>
                    <h3 className="text-xl font-semibold mb-4 text-white/90 flex items-center">
                        <span className="bg-white/10 p-1.5 rounded-lg mr-2">🥗</span>
                        Ingredients
                    </h3>
                    <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {ingredients.map((ingredient, idx) => (
                            <li key={idx} className="flex items-center text-white/70 bg-white/5 p-3 rounded-lg border border-white/5 hover:border-white/10 transition-colors">
                                <span className="w-1.5 h-1.5 rounded-full bg-primary mr-3" />
                                {ingredient}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Separator */}
                <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

                {/* Instructions Section */}
                <div>
                    <h3 className="text-xl font-semibold mb-4 text-white/90 flex items-center">
                        <span className="bg-white/10 p-1.5 rounded-lg mr-2">🍳</span>
                        Instructions
                    </h3>
                    <div className="space-y-6">
                        {steps.map((step, idx) => (
                            <div key={idx} className="group flex gap-4">
                                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/10 border border-white/10 flex items-center justify-center font-bold text-sm group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                                    {idx + 1}
                                </div>
                                <p className="text-white/70 leading-relaxed pt-1">
                                    {step}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Metadata / Footer if exists */}
                {recipe.metadata && (
                    <>
                        <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
                        <div className="flex gap-4 text-sm text-white/50">
                            {/* Example metadata rendering if standard keys exist */}
                            {recipe.metadata.prep_time && (
                                <div className="flex items-center">
                                    <Clock className="w-4 h-4 mr-1" /> {recipe.metadata.prep_time}
                                </div>
                            )}
                            {recipe.metadata.servings && (
                                <div className="flex items-center">
                                    <Users className="w-4 h-4 mr-1" /> {recipe.metadata.servings}
                                </div>
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    )
}
