"use client";

import {
  Activity,
  Database,
  Clock,
  LayoutTemplate,
  Network,
  History,
} from "lucide-react";

export default function DevMemoryInspector() {
  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-300 font-mono p-8">
      <header className="mb-8 border-b border-neutral-800 pb-4">
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <Database className="text-blue-500" /> Cognee Memory Inspector
        </h1>
        <p className="text-sm mt-2 opacity-60">
          Developer tool for visualizing exact retrieval mechanisms.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Memory Graph */}
        <div className="lg:col-span-2 space-y-8">
          <section className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 h-[500px] flex flex-col">
            <h2 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
              <Network className="w-5 h-5 text-purple-500" /> Live Graph
            </h2>
            <div className="flex-1 border border-neutral-800 rounded-lg bg-black/50 flex items-center justify-center relative overflow-hidden">
              <p className="text-neutral-500 text-sm animate-pulse">
                Waiting for graph data...
              </p>
              {/* Visualizer will mount here */}
            </div>
          </section>

          <section className="bg-neutral-900 border border-neutral-800 rounded-xl p-6">
            <h2 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5 text-green-500" /> Recent Retrievals
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs uppercase bg-neutral-800 text-neutral-400">
                  <tr>
                    <th className="px-4 py-3 rounded-tl-lg">Query</th>
                    <th className="px-4 py-3">Latency</th>
                    <th className="px-4 py-3">Nodes Hit</th>
                    <th className="px-4 py-3 rounded-tr-lg">Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-neutral-800">
                    <td className="px-4 py-3">
                      "What changed in Dad's health?"
                    </td>
                    <td className="px-4 py-3">124ms</td>
                    <td className="px-4 py-3">14</td>
                    <td className="px-4 py-3 text-green-400">92%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </div>

        {/* Right Column: Context Inspector */}
        <div className="space-y-8">
          <section className="bg-neutral-900 border border-neutral-800 rounded-xl p-6">
            <h2 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
              <LayoutTemplate className="w-5 h-5 text-orange-500" /> Context
              Package
            </h2>
            <pre className="bg-black/50 p-4 rounded-lg overflow-x-auto text-xs text-neutral-400">
              {`{
  "active_family": "sharma_uuid",
  "active_member": "anil_uuid",
  "recent_events": [
    "diagnosis_diabetes",
    "prescription_metformin"
  ],
  "retrieved_nodes": [
    "node_7382",
    "node_9182"
  ]
}`}
            </pre>
          </section>

          <section className="bg-neutral-900 border border-neutral-800 rounded-xl p-6">
            <h2 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
              <History className="w-5 h-5 text-yellow-500" /> Raw Cognee Log
            </h2>
            <div className="space-y-3">
              <div className="text-xs font-mono bg-black/30 p-2 rounded border-l-2 border-green-500">
                [10:14:02] MATCH node_7382 (Diabetes) &gt; user_anil
              </div>
              <div className="text-xs font-mono bg-black/30 p-2 rounded border-l-2 border-blue-500">
                [10:14:03] EMBED query "health changes"
              </div>
              <div className="text-xs font-mono bg-black/30 p-2 rounded border-l-2 border-red-500">
                [10:14:04] ALERT metric_threshold_exceeded (HbA1c=8.2)
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
