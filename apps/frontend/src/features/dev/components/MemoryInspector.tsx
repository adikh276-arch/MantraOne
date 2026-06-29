"use client";

import React from "react";

export function MemoryInspector() {
  if (process.env.NODE_ENV === "production") return null;

  return (
    <div className="p-6 bg-stone-900 text-stone-100 rounded-2xl font-mono text-sm shadow-xl">
      <div className="flex items-center justify-between mb-4 border-b border-stone-700 pb-4">
        <h2 className="text-lg font-bold text-white">
          Memory Inspector (Cognee Graph)
        </h2>
        <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded">
          Live
        </span>
      </div>

      <div className="space-y-4">
        <div>
          <h3 className="text-stone-400 mb-2">// Node: Member:John_Smith</h3>
          <pre className="bg-black/50 p-4 rounded-xl overflow-x-auto text-stone-300">
            {`{
  "id": "mem_123",
  "label": "Person",
  "properties": {
    "name": "John Smith",
    "age": 45,
    "confidence_score": 0.92
  },
  "edges": [
    { "type": "HAS_DIAGNOSIS", "target": "diag_htn", "weight": 1.0 },
    { "type": "TAKES_MEDICATION", "target": "med_telmisartan", "weight": 1.0 }
  ]
}`}
          </pre>
        </div>
      </div>
    </div>
  );
}
