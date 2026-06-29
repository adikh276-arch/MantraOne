"use client";

import React from "react";
import { EventCard, TimelineEvent } from "./EventCards";

interface Chapter {
  title: string;
  period: string;
  events: TimelineEvent[];
}

const mockChapters: Chapter[] = [
  {
    title: "Stable Period",
    period: "Current",
    events: [
      {
        id: "1",
        type: "insight",
        date: "2026-06-25",
        title: "BP Trending Normal",
        description:
          "Recent vitals show stable blood pressure over the last 14 days.",
      },
    ],
  },
  {
    title: "Monitoring",
    period: "May 2026",
    events: [
      {
        id: "2",
        type: "lab",
        date: "2026-05-15",
        title: "Lipid Panel",
        description: "LDL elevated at 145 mg/dL. Recommended dietary changes.",
      },
      {
        id: "3",
        type: "visit",
        date: "2026-05-10",
        title: "Cardiologist Follow-up",
        description: "Dr. Sharma noted mild hypertension.",
      },
    ],
  },
  {
    title: "Diagnosis",
    period: "April 2026",
    events: [
      {
        id: "4",
        type: "medication",
        date: "2026-04-20",
        title: "Started Telmisartan",
        description: "40mg daily for hypertension management.",
      },
      {
        id: "5",
        type: "diagnosis",
        date: "2026-04-18",
        title: "Essential Hypertension",
        description: "Diagnosed after 3 consecutive elevated readings.",
      },
    ],
  },
];

export function TimelineFeed() {
  return (
    <div className="max-w-2xl mx-auto py-12 px-6">
      <div className="mb-12">
        <h2 className="text-3xl font-semibold text-stone-900 tracking-tight">
          Health Story
        </h2>
        <p className="text-stone-500 mt-2">
          A longitudinal view of your family's health journey.
        </p>
      </div>

      <div className="space-y-12">
        {mockChapters.map((chapter, idx) => (
          <div key={idx} className="relative">
            <div className="sticky top-0 bg-stone-100/90 backdrop-blur-md py-4 z-20 mb-4 border-b border-stone-200 flex justify-between items-end">
              <h3 className="text-lg font-semibold text-stone-900">
                {chapter.title}
              </h3>
              <span className="text-sm font-medium text-stone-500">
                {chapter.period}
              </span>
            </div>

            <div>
              {chapter.events.map((event) => (
                <EventCard key={event.id} event={event} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
