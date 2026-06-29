'use client';

import React from 'react';

// For this sprint, we'll implement a lightweight markdown renderer that intercepts specific JSON-like blocks
// to render rich cards inline, while standard text renders as paragraphs.
// In a full implementation, we'd use `react-markdown` with custom components.

interface MessageRendererProps {
  content: string;
}

export function MessageRenderer({ content }: MessageRendererProps) {
  // Simple check: if it looks like a rich card payload (e.g. `[MedicationCard: ...]`)
  if (content.includes('[MedicationCard:')) {
    const cardDataStr = content.match(/\[MedicationCard:\s*(.*?)\]/)?.[1];
    try {
      const data = JSON.parse(cardDataStr || '{}');
      return (
        <div className="space-y-2">
          <p className="text-stone-800 leading-relaxed text-sm md:text-base">
            {content.replace(/\[MedicationCard:\s*.*?\]/, '').trim()}
          </p>
          <div className="bg-orange-50 border border-orange-100 p-4 rounded-xl shadow-sm mt-2">
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-medium text-orange-900">{data.name}</h4>
                <p className="text-sm text-orange-700">{data.dosage} • {data.frequency}</p>
              </div>
              <span className="px-2 py-1 bg-white text-xs font-medium text-orange-600 rounded-md shadow-sm border border-orange-50">
                Active
              </span>
            </div>
            {data.reason && <p className="text-xs text-orange-600 mt-3 border-t border-orange-100/50 pt-2">{data.reason}</p>}
          </div>
        </div>
      );
    } catch (e) {
      // Fallback if parsing fails
    }
  }

  // Fallback normal text
  return <p className="text-stone-800 leading-relaxed text-sm md:text-base whitespace-pre-wrap">{content}</p>;
}
