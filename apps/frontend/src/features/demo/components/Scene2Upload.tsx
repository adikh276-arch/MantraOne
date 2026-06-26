"use client";

import { motion } from "framer-motion";
import { UploadCloud, FileText, Database, Activity, CheckCircle } from "lucide-react";
import { useState, useEffect } from "react";

type UploadPhase = "idle" | "uploading" | "processing" | "extracting" | "creating_memory" | "done";

export function Scene2Upload({ onNext }: { onNext: () => void }) {
  const [phase, setPhase] = useState<UploadPhase>("idle");

  useEffect(() => {
    if (phase === "uploading") setTimeout(() => setPhase("processing"), 1500);
    if (phase === "processing") setTimeout(() => setPhase("extracting"), 2000);
    if (phase === "extracting") setTimeout(() => setPhase("creating_memory"), 2500);
    if (phase === "creating_memory") setTimeout(() => setPhase("done"), 2000);
  }, [phase]);

  return (
    <div className="w-full max-w-3xl flex flex-col items-center min-h-[60vh] justify-center">
      {phase === "idle" && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex flex-col items-center"
        >
          <div className="w-32 h-32 rounded-full bg-neutral-900 border border-neutral-800 flex items-center justify-center mb-8 relative">
             <FileText className="w-12 h-12 text-white" />
             <div className="absolute -bottom-2 -right-2 bg-red-500 text-xs px-2 py-1 rounded-full font-bold">PDF</div>
          </div>
          <h3 className="text-3xl font-medium text-white mb-2">Dad's Medical Report</h3>
          <p className="text-neutral-500 mb-8 font-mono">diabetes_lab.pdf • 1.2 MB</p>
          <button
            onClick={() => setPhase("uploading")}
            className="flex items-center gap-3 bg-white text-black px-8 py-4 rounded-full font-medium hover:scale-105 transition-transform"
          >
            <UploadCloud className="w-5 h-5" />
            Upload to Family Memory
          </button>
        </motion.div>
      )}

      {phase !== "idle" && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="w-full"
        >
          <div className="flex flex-col items-center mb-16 relative">
             <div className="absolute inset-0 bg-blue-500/20 blur-[100px] rounded-full" />
             <h3 className="text-3xl font-medium text-white mb-3 tracking-tight z-10">Building Context</h3>
             <p className="text-neutral-400 text-lg z-10">Weaving new medical data into the family graph</p>
          </div>

          <div className="space-y-4 max-w-2xl mx-auto">
             <StatusRow 
                icon={<UploadCloud className="w-5 h-5" />} 
                title="Uploading document securely" 
                active={phase === "uploading"} 
                done={["processing", "extracting", "creating_memory", "done"].includes(phase)} 
             />
             <StatusRow 
                icon={<Activity className="w-5 h-5" />} 
                title="Processing text via OCR & NLP" 
                active={phase === "processing"} 
                done={["extracting", "creating_memory", "done"].includes(phase)} 
             />
             <StatusRow 
                icon={<FileText className="w-5 h-5" />} 
                title="Extracting entities (HbA1c, Metformin)" 
                active={phase === "extracting"} 
                done={["creating_memory", "done"].includes(phase)} 
             />
             <StatusRow 
                icon={<Database className="w-5 h-5" />} 
                title="Updating Living Memory Graph" 
                active={phase === "creating_memory"} 
                done={phase === "done"} 
             />
          </div>

          {phase === "done" && (
             <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="mt-16 flex justify-center"
             >
                <button 
                  onClick={onNext}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-full font-medium transition-colors"
                >
                  View Memory Graph
                </button>
             </motion.div>
          )}
        </motion.div>
      )}
    </div>
  );
}

function StatusRow({ icon, title, active, done }: { icon: React.ReactNode, title: string, active: boolean, done: boolean }) {
  return (
    <motion.div 
       initial={false}
       animate={{ 
          scale: active ? 1.02 : 1,
          opacity: (active || done) ? 1 : 0.4
       }}
       transition={{ type: "spring", stiffness: 300, damping: 20 }}
       className={`flex items-center gap-6 p-5 rounded-2xl border transition-colors duration-500 relative overflow-hidden ${active ? 'bg-blue-900/20 border-blue-500/40 shadow-[0_0_30px_rgba(59,130,246,0.15)]' : done ? 'bg-neutral-900/80 border-neutral-800' : 'bg-transparent border-transparent'}`}
    >
       {active && <motion.div layoutId="active-glow" className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-transparent z-0" />}
       
       <div className={`relative z-10 w-12 h-12 rounded-full flex items-center justify-center transition-colors duration-500 ${active ? 'bg-blue-500 text-white shadow-[0_0_20px_rgba(59,130,246,0.5)]' : done ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-neutral-800 text-neutral-500'}`}>
         {done ? <CheckCircle className="w-6 h-6" /> : (
            <motion.div animate={active ? { scale: [1, 1.2, 1] } : {}} transition={{ repeat: Infinity, duration: 2 }}>
               {icon}
            </motion.div>
         )}
       </div>
       <div className="flex-1 relative z-10">
          <h4 className={`text-xl tracking-tight transition-colors duration-500 ${active ? 'text-white font-medium' : done ? 'text-neutral-300' : 'text-neutral-600'}`}>{title}</h4>
       </div>
       
       {active && (
          <div className="relative z-10 w-6 h-6 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
       )}
    </motion.div>
  );
}
