"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Network, ZoomIn, ZoomOut, Maximize, ArrowRight, Activity, FileText, User, Pill, Stethoscope, AlertCircle } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';

// Dummy static graph for presentation mode
const PRESENTATION_NODES = [
  { id: '1', label: 'Anil Sharma', type: 'person' },
  { id: '2', label: 'Diabetes Type 2', type: 'condition' },
  { id: '3', label: 'HbA1c 8.2%', type: 'metric' },
  { id: '4', label: 'Metformin 500mg', type: 'medication' },
  { id: '5', label: 'Dr. Gupta', type: 'doctor' },
];
const PRESENTATION_EDGES = [
  { source: '1', target: '2', label: 'diagnosed_with' },
  { source: '1', target: '3', label: 'has_metric' },
  { source: '1', target: '4', label: 'prescribed' },
  { source: '5', target: '4', label: 'prescribed_by' },
];

export function Scene3Graph({ onNext, mode }: { onNext: () => void, mode: "live" | "presentation" }) {
  const [nodes, setNodes] = useState<any[]>([]);
  const [edges, setEdges] = useState<any[]>([]);
  const [ready, setReady] = useState(false);
  const [zoom, setZoom] = useState(1);

  // We need to fetch the family ID first if in live mode, or hardcode the search for 'sharma'
  const { data: familyData } = useQuery({
    queryKey: ['family'],
    queryFn: async () => {
      const res = await fetch('http://localhost:8000/v1/families/');
      if (!res.ok) throw new Error("Failed");
      const families = await res.json();
      return families[0]; // Assuming Sharma is the first/only family in the golden dataset
    },
    enabled: mode === 'live'
  });

  const { data: graphData } = useQuery({
    queryKey: ['graph', familyData?.id],
    queryFn: async () => {
      const res = await fetch(`http://localhost:8000/v1/memory/graph?family_id=${familyData?.id}`);
      if (!res.ok) throw new Error("Failed");
      return await res.json();
    },
    enabled: mode === 'live' && !!familyData?.id
  });

  useEffect(() => {
    if (mode === "presentation") {
      const timers: NodeJS.Timeout[] = [];
      PRESENTATION_NODES.forEach((node, idx) => {
        timers.push(setTimeout(() => {
          setNodes(prev => [...prev, node]);
        }, idx * 800));
      });
      timers.push(setTimeout(() => {
        setEdges(PRESENTATION_EDGES);
        setReady(true);
      }, PRESENTATION_NODES.length * 800 + 500));
      return () => timers.forEach(clearTimeout);
    } else if (mode === "live" && graphData) {
      // Animate the real nodes coming in
      const timers: NodeJS.Timeout[] = [];
      setNodes([]);
      setEdges([]);
      setReady(false);
      
      graphData.nodes.forEach((node: any, idx: number) => {
        timers.push(setTimeout(() => {
          setNodes(prev => [...prev, node]);
        }, Math.min(idx * 300, 2000))); // Cap animation time for large graphs
      });
      
      timers.push(setTimeout(() => {
        setEdges(graphData.edges);
        setReady(true);
      }, Math.min(graphData.nodes.length * 300, 2000) + 500));
      return () => timers.forEach(clearTimeout);
    }
  }, [mode, graphData]);

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'person': return <User className="w-6 h-6 text-blue-400" />;
      case 'condition': return <Activity className="w-6 h-6 text-red-400" />;
      case 'metric': return <AlertCircle className="w-6 h-6 text-orange-400" />;
      case 'medication': return <Pill className="w-6 h-6 text-green-400" />;
      case 'doctor': return <Stethoscope className="w-6 h-6 text-purple-400" />;
      case 'document': return <FileText className="w-6 h-6 text-indigo-400" />;
      default: return <User className="w-6 h-6 text-neutral-400" />;
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
          {/* Animated Edge Lines (Only drawn if nodes actually exist in the UI) */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
            <AnimatePresence>
              {edges.map((edge, i) => {
                 // For presentation mode, we hardcode positions. For live mode, we might need a force graph library, but we can fake positions via index for demo if we don't have a layout engine
                 const getMockPos = (id: string) => {
                    const isPres = mode === "presentation";
                    if (isPres) {
                      if (id === '1') return { x: 300, y: 250 };
                      if (id === '2') return { x: 500, y: 150 };
                      if (id === '3') return { x: 500, y: 350 };
                      if (id === '4') return { x: 100, y: 250 };
                      if (id === '5') return { x: 100, y: 100 };
                    } else {
                      // VERY basic deterministic positioning for Live Mode just for the 2D canvas demo
                      const idx = nodes.findIndex(n => n.id === id);
                      if (idx === -1) return { x: 0, y: 0 };
                      const angle = (idx / nodes.length) * Math.PI * 2;
                      const radius = 150;
                      return { x: 300 + Math.cos(angle) * radius, y: 250 + Math.sin(angle) * radius };
                    }
                    return { x: 300, y: 250 };
                 };
                 
                 const sourcePos = getMockPos(edge.source);
                 const targetPos = getMockPos(edge.target);
                 if (sourcePos.x === 0 || targetPos.x === 0) return null; // skip if node not found yet

                 return (
                  <motion.line
                    key={i}
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{ pathLength: 1, opacity: 0.2 }}
                    transition={{ duration: 1, delay: i * 0.2 }}
                    x1={sourcePos.x} y1={sourcePos.y} x2={targetPos.x} y2={targetPos.y}
                    stroke="#60A5FA"
                    strokeWidth="2"
                  />
                );
              })}
            </AnimatePresence>
          </svg>

          {/* Nodes */}
          {nodes.map((node, i) => {
            const getMockPos = (id: string) => {
               const isPres = mode === "presentation";
               if (isPres) {
                 if (id === '1') return { left: '300px', top: '250px' };
                 if (id === '2') return { left: '500px', top: '150px' };
                 if (id === '3') return { left: '500px', top: '350px' };
                 if (id === '4') return { left: '100px', top: '250px' };
                 if (id === '5') return { left: '100px', top: '100px' };
               } else {
                 const angle = (i / nodes.length) * Math.PI * 2;
                 const radius = 150;
                 return { left: `${300 + Math.cos(angle) * radius}px`, top: `${250 + Math.sin(angle) * radius}px` };
               }
               return { left: '300px', top: '250px' };
            };
            
            return (
              <motion.div
                key={node.id}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: "spring", stiffness: 200, damping: 20 }}
                className={`absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-3 z-10 ${node.id === '1' ? 'z-20' : ''}`}
                style={getMockPos(node.id)}
              >
                <div className={`w-16 h-16 rounded-full flex items-center justify-center border-4 ${node.id === '1' ? 'bg-blue-900 border-blue-500 shadow-[0_0_30px_rgba(59,130,246,0.3)]' : 'bg-neutral-900 border-neutral-800'}`}>
                   {getNodeIcon(node.type)}
                </div>
                <div className="bg-black/80 backdrop-blur border border-neutral-800 px-4 py-2 rounded-full whitespace-nowrap">
                   <p className={`text-sm font-medium ${node.id === '1' ? 'text-white' : 'text-neutral-300'}`}>{node.label}</p>
                   <p className="text-[10px] text-neutral-500 uppercase tracking-widest text-center mt-0.5">{node.type}</p>
                </div>
              </motion.div>
            );
          })}
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
