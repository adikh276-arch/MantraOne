"use client";

import { motion } from "framer-motion";
import { Network, ZoomIn, ZoomOut, Maximize } from "lucide-react";
import { useState } from "react";

const nodes = [
  { id: "anil", label: "Anil Sharma", type: "person", x: 400, y: 300, delay: 0.1 },
  { id: "diabetes", label: "Type 2 Diabetes", type: "condition", x: 250, y: 150, delay: 0.5 },
  { id: "hba1c", label: "HbA1c: 8.2%", type: "metric", x: 100, y: 250, delay: 0.9 },
  { id: "metformin", label: "Metformin 500mg", type: "medication", x: 550, y: 150, delay: 1.3 },
  { id: "report", label: "Diabetes Lab Report", type: "document", x: 300, y: 450, delay: 1.7 },
  { id: "doctor", label: "Dr. Gupta", type: "doctor", x: 550, y: 450, delay: 2.1 },
];

const edges = [
  { source: "anil", target: "diabetes" },
  { source: "diabetes", target: "hba1c" },
  { source: "anil", target: "metformin" },
  { source: "anil", target: "report" },
  { source: "diabetes", target: "metformin" },
  { source: "report", target: "hba1c" },
  { source: "anil", target: "doctor" }
];

export function Scene3Graph({ onNext }: { onNext: () => void }) {
  const [zoom, setZoom] = useState(1);

  const getNodeColor = (type: string) => {
    switch(type) {
      case "person": return "bg-blue-500 border-blue-400";
      case "condition": return "bg-red-500 border-red-400";
      case "metric": return "bg-orange-500 border-orange-400";
      case "medication": return "bg-green-500 border-green-400";
      case "document": return "bg-purple-500 border-purple-400";
      case "doctor": return "bg-cyan-500 border-cyan-400";
      default: return "bg-neutral-500 border-neutral-400";
    }
  };

  return (
    <div className="w-full h-[80vh] flex flex-col relative">
      <div className="absolute top-0 left-0 p-8 z-10 pointer-events-none">
        <h2 className="text-3xl font-medium text-white flex items-center gap-3">
          <Network className="text-blue-500" /> Living Memory Graph
        </h2>
        <p className="text-neutral-400 mt-2 max-w-md">
          MantraOne continuously weaves new medical data into a persistent family graph. 
          Relationships are mapped automatically.
        </p>
      </div>

      <div className="absolute bottom-8 right-8 z-10 flex gap-2">
         <button onClick={() => setZoom(z => Math.min(z + 0.2, 2))} className="p-3 bg-neutral-900 border border-neutral-800 rounded-lg hover:bg-neutral-800 transition-colors"><ZoomIn className="w-5 h-5" /></button>
         <button onClick={() => setZoom(z => Math.max(z - 0.2, 0.5))} className="p-3 bg-neutral-900 border border-neutral-800 rounded-lg hover:bg-neutral-800 transition-colors"><ZoomOut className="w-5 h-5" /></button>
         <button onClick={() => setZoom(1)} className="p-3 bg-neutral-900 border border-neutral-800 rounded-lg hover:bg-neutral-800 transition-colors"><Maximize className="w-5 h-5" /></button>
      </div>

      <div className="flex-1 w-full bg-[#0a0a0a] rounded-2xl border border-neutral-800 overflow-hidden relative cursor-move">
        <motion.div 
          className="w-full h-full origin-center"
          animate={{ scale: zoom }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        >
          {/* Edges */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {edges.map((edge, i) => {
              const sourceNode = nodes.find(n => n.id === edge.source)!;
              const targetNode = nodes.find(n => n.id === edge.target)!;
              return (
                <motion.line 
                  key={i}
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: 1, opacity: 0.3 }}
                  transition={{ delay: Math.max(sourceNode.delay, targetNode.delay) + 0.3, duration: 1 }}
                  x1={sourceNode.x} y1={sourceNode.y} x2={targetNode.x} y2={targetNode.y}
                  stroke="#525252" strokeWidth="2"
                />
              );
            })}
          </svg>

          {/* Nodes */}
          {nodes.map(node => (
            <motion.div
              key={node.id}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: node.delay, type: "spring", stiffness: 200, damping: 20 }}
              className={`absolute flex items-center justify-center p-4 rounded-full border-2 bg-opacity-20 backdrop-blur-md text-sm font-medium text-white shadow-[0_0_30px_rgba(0,0,0,0.5)] ${getNodeColor(node.type)}`}
              style={{ left: node.x - 50, top: node.y - 25, width: 100, height: 50 }}
            >
              <span className="truncate w-full text-center">{node.label}</span>
            </motion.div>
          ))}
        </motion.div>
      </div>

      <motion.div 
         initial={{ opacity: 0 }} 
         animate={{ opacity: 1 }} 
         transition={{ delay: 4 }}
         className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10"
      >
        <button 
          onClick={onNext}
          className="bg-white text-black px-8 py-4 rounded-full font-medium hover:scale-105 transition-transform shadow-2xl shadow-white/10"
        >
          Ask a Question
        </button>
      </motion.div>
    </div>
  );
}
