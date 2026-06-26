"use client";

import { motion } from "framer-motion";
import { HeartPulse, Stethoscope, FileText, ArrowRight } from "lucide-react";
import { useState, useEffect } from "react";

export function Scene6Escalation({ onRestart }: { onRestart: () => void }) {
  const [phase, setPhase] = useState<"alerting" | "briefing">("alerting");

  useEffect(() => {
    if (phase === "alerting") {
       setTimeout(() => setPhase("briefing"), 3000);
    }
  }, [phase]);

  return (
    <div className="w-full max-w-4xl flex flex-col items-center">
      {phase === "alerting" && (
        <motion.div 
          key="alerting"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex flex-col items-center justify-center min-h-[50vh]"
        >
          <div className="relative">
             <div className="absolute inset-0 bg-red-500 rounded-full animate-ping opacity-20" />
             <div className="bg-red-500/10 p-6 rounded-full border border-red-500/30 text-red-500 relative z-10">
                <HeartPulse className="w-16 h-16 animate-pulse" />
             </div>
          </div>
          <h2 className="text-3xl font-medium text-red-400 mt-8 mb-2">Automated Escalation Triggered</h2>
          <p className="text-neutral-400">Coordinator detected critical HbA1c deviation (8.2%)</p>
          <p className="text-neutral-500 mt-4 animate-pulse">Generating Doctor Consultation Brief...</p>
        </motion.div>
      )}

      {phase === "briefing" && (
        <motion.div 
          key="briefing"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full"
        >
          <div className="w-full flex items-center justify-between mb-8">
             <h2 className="text-3xl font-medium text-white flex items-center gap-3">
               <Stethoscope className="text-blue-500" /> Doctor Consultation Brief
             </h2>
             <span className="bg-red-500/10 text-red-400 border border-red-500/20 px-4 py-1.5 rounded-full text-sm font-medium">
               High Priority
             </span>
          </div>

          <div className="bg-[#0a0a0a] border border-neutral-800 rounded-3xl p-12 relative overflow-hidden shadow-2xl">
             <div className="absolute top-0 right-0 bg-neutral-900 border-b border-l border-neutral-800 px-6 py-2 rounded-bl-2xl text-xs font-mono text-neutral-500 tracking-widest uppercase">
                CONFIDENTIAL • MANTRAONE
             </div>

             <div className="grid grid-cols-2 gap-12 mb-12 border-b border-neutral-800 pb-12">
                <div>
                   <p className="text-neutral-500 text-sm mb-2 uppercase tracking-widest font-mono">Patient Profile</p>
                   <p className="text-3xl text-white font-medium tracking-tight">Anil Sharma <span className="text-neutral-500 font-normal">(52, Male)</span></p>
                </div>
                <div>
                   <p className="text-neutral-500 text-sm mb-2 uppercase tracking-widest font-mono">Primary Concern</p>
                   <p className="text-2xl text-red-400 font-medium tracking-tight">Uncontrolled Type 2 Diabetes</p>
                </div>
             </div>

             <div className="space-y-10">
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                   <h4 className="text-xl text-white font-medium mb-4 flex items-center gap-3">
                     <FileText className="w-5 h-5 text-neutral-500" /> AI Executive Summary
                   </h4>
                   <div className="text-neutral-300 leading-relaxed text-lg bg-neutral-900/50 p-8 rounded-3xl border border-neutral-800/80 font-light">
                     Patient's HbA1c has sharply escalated to <strong className="text-red-400 font-semibold">8.2%</strong> (from 6.8% in previous checkup). Fasting glucose is currently 165 mg/dL. The patient reports worsening fatigue over the past 3 weeks. 
                   </div>
                </motion.div>

                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
                   <h4 className="text-xl text-white font-medium mb-4">Contextual History</h4>
                   <ul className="space-y-4 text-neutral-400 list-none font-light">
                      <li className="flex items-start gap-4">
                         <div className="mt-1 w-2 h-2 rounded-full bg-neutral-700" />
                         <div><strong className="text-neutral-300 font-medium">Sep 02:</strong> Vitals were stable. No medication was required at that time.</div>
                      </li>
                      <li className="flex items-start gap-4">
                         <div className="mt-1 w-2 h-2 rounded-full bg-red-500" />
                         <div><strong className="text-neutral-300 font-medium">Oct 15:</strong> Labs returned abnormal. Metformin 500mg BD recommended.</div>
                      </li>
                   </ul>
                </motion.div>

                <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 1.0 }} className="bg-blue-950/20 border border-blue-500/30 rounded-3xl p-8 mt-12 relative overflow-hidden">
                   <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-transparent pointer-events-none" />
                   <h4 className="text-blue-400 font-medium mb-3 text-lg">Recommended Action for Doctor</h4>
                   <p className="text-blue-200 leading-relaxed font-light text-lg">
                     Evaluate immediate initiation of Metformin 500mg. Review patient's lifestyle and stress factors (sleep data indicates reduced hours over the past week).
                   </p>
                </motion.div>
             </div>
          </div>

          <div className="mt-16 flex flex-col items-center">
             <p className="text-neutral-500 text-lg mb-6 text-center max-w-lg">
               This is what proactive family healthcare looks like. MantraOne doesn't just remember—it acts.
             </p>
             <button 
               onClick={onRestart}
               className="bg-white text-black px-8 py-4 rounded-full font-medium hover:scale-105 transition-transform flex items-center gap-2"
             >
               Restart Demo <ArrowRight className="w-4 h-4" />
             </button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
