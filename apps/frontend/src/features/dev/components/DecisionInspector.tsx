"use client";

import React from "react";

export function DecisionInspector() {
  if (process.env.NODE_ENV === "production") return null;

  return (
    <div className="p-6 bg-stone-900 text-stone-100 rounded-2xl font-mono text-sm shadow-xl mt-4">
      <div className="flex items-center justify-between mb-4 border-b border-stone-700 pb-4">
        <h2 className="text-lg font-bold text-white">Decision Engine</h2>
        <span className="px-2 py-1 bg-amber-500/20 text-amber-400 rounded">
          Active
        </span>
      </div>

      <div className="space-y-4">
        <div>
          <h3 className="text-stone-400 mb-2">// Queue State (Top Action)</h3>
          <pre className="bg-black/50 p-4 rounded-xl overflow-x-auto text-stone-300">
            {`{
  "action_type": "ASK_QUESTION",
  "priority": 85,
  "reason": "Missing context for Telmisartan prescription",
  "context": {
    "medication": "Telmisartan 40mg",
    "missing_edge": "DIAGNOSIS"
  },
  "expected_information_gain": 0.4
}`}
          </pre>
        </div>
      </div>
    </div>
  );
}
