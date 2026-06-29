"use client";

import React from "react";
import { motion } from "framer-motion";

export interface TimelineEvent {
  id: string;
  type: "diagnosis" | "medication" | "lab" | "visit" | "insight";
  date: string;
  title: string;
  description: string;
  metadata?: any;
}

interface EventCardsProps {
  event: TimelineEvent;
}

export function EventCard({ event }: EventCardsProps) {
  const getIcon = () => {
    switch (event.type) {
      case "diagnosis":
        return "🏥";
      case "medication":
        return "💊";
      case "lab":
        return "🔬";
      case "visit":
        return "🩺";
      case "insight":
        return "💡";
      default:
        return "📝";
    }
  };

  const getColor = () => {
    switch (event.type) {
      case "diagnosis":
        return "bg-red-50 border-red-100 text-red-900";
      case "medication":
        return "bg-orange-50 border-orange-100 text-orange-900";
      case "lab":
        return "bg-blue-50 border-blue-100 text-blue-900";
      case "visit":
        return "bg-stone-50 border-stone-200 text-stone-900";
      case "insight":
        return "bg-emerald-50 border-emerald-100 text-emerald-900";
      default:
        return "bg-stone-50 border-stone-200 text-stone-900";
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      className={`relative pl-8 py-4 before:absolute before:left-[11px] before:top-0 before:bottom-0 before:w-0.5 before:bg-stone-200`}
    >
      <div className="absolute left-0 top-6 w-6 h-6 bg-white border-2 border-stone-200 rounded-full flex items-center justify-center text-xs z-10 shadow-sm">
        {getIcon()}
      </div>

      <div
        className={`p-4 rounded-xl border ${getColor()} shadow-sm transition-transform hover:-translate-y-1 hover:shadow-md cursor-pointer`}
      >
        <div className="flex justify-between items-start mb-2">
          <h4 className="font-medium text-base">{event.title}</h4>
          <span className="text-xs font-medium opacity-70">
            {new Date(event.date).toLocaleDateString()}
          </span>
        </div>
        <p className="text-sm opacity-80 leading-relaxed">
          {event.description}
        </p>

        {event.metadata && (
          <div className="mt-3 pt-3 border-t border-black/5">
            <span className="text-xs font-semibold opacity-70">
              Context attached
            </span>
          </div>
        )}
      </div>
    </motion.div>
  );
}
