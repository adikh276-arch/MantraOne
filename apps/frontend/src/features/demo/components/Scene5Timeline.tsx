"use client";

import { motion } from "framer-motion";
import { Clock, AlertTriangle, CheckCircle, FileText } from "lucide-react";

export function Scene5Timeline({ onNext }: { onNext: () => void }) {
  return (
    <div className="w-full max-w-4xl flex flex-col items-center">
      <div className="w-full text-center mb-16">
         <h2 className="text-4xl font-medium text-white mb-4">Family Health Timeline</h2>
         <p className="text-neutral-400 text-lg">Every memory grounds MantraOne in your history.</p>
      </div>

      <div className="w-full max-w-2xl relative">
         <div className="absolute top-0 bottom-0 left-[39px] w-[2px] bg-neutral-800" />
         
         <div className="space-y-12">
            <TimelineItem 
               icon={<AlertTriangle className="w-5 h-5 text-red-500" />}
               date="Today (Oct 15, 2026)"
               title="HbA1c Elevated to 8.2%"
               description="New diagnosis of uncontrolled Type 2 Diabetes based on recent lab report. Metformin 500mg prescribed."
               badge="Diabetes Lab Report"
               delay={0.2}
               active
            />
            <TimelineItem 
               icon={<CheckCircle className="w-5 h-5 text-green-500" />}
               date="Sep 02, 2026"
               title="Routine Consultation"
               description="Vitals stable. Fasting glucose at 105 mg/dL. No medication required at this time."
               badge="Dr. Gupta Visit"
               delay={0.6}
            />
            <TimelineItem 
               icon={<FileText className="w-5 h-5 text-blue-500" />}
               date="Jan 15, 2026"
               title="Annual Physical"
               description="Overall health marked as excellent. Recommended lifestyle changes for weight management."
               badge="Annual Review"
               delay={1.0}
            />
         </div>
      </div>

      <motion.div 
         initial={{ opacity: 0 }}
         animate={{ opacity: 1 }}
         transition={{ delay: 2.0 }}
         className="mt-20"
      >
         <button 
           onClick={onNext}
           className="bg-red-600/10 border border-red-600/50 text-red-500 hover:bg-red-600/20 px-8 py-4 rounded-full font-medium transition-colors flex items-center gap-2"
         >
           <AlertTriangle className="w-5 h-5" /> Simulate Escalation Trigger
         </button>
      </motion.div>
    </div>
  );
}

function TimelineItem({ icon, date, title, description, badge, delay, active = false }: any) {
  return (
    <motion.div 
       initial={{ opacity: 0, y: 30 }}
       animate={{ opacity: 1, y: 0 }}
       transition={{ delay, type: "spring", stiffness: 200, damping: 25 }}
       className={`relative pl-24 group ${active ? 'opacity-100' : 'opacity-60 hover:opacity-100 transition-opacity duration-500'}`}
    >
       <div className={`absolute left-[20px] top-1 w-10 h-10 rounded-full flex items-center justify-center border-4 border-neutral-950 transition-colors duration-500 z-10 ${active ? 'bg-red-500/20 text-red-500 shadow-[0_0_20px_rgba(239,68,68,0.4)] border-neutral-900' : 'bg-neutral-900 text-neutral-500 group-hover:bg-neutral-800'}`}>
          {icon}
       </div>
       
       <div className={`rounded-3xl p-8 transition-colors duration-500 border relative overflow-hidden ${active ? 'bg-red-950/10 border-red-900/30' : 'bg-[#0f0f0f] border-neutral-800 group-hover:border-neutral-700'}`}>
          {active && <div className="absolute inset-0 bg-gradient-to-r from-red-500/5 to-transparent pointer-events-none" />}
          
          <p className="text-sm font-mono text-neutral-500 mb-3 tracking-widest uppercase">{date}</p>
          <h4 className={`text-2xl font-semibold mb-4 tracking-tight ${active ? 'text-red-400' : 'text-white'}`}>{title}</h4>
          <p className="text-neutral-400 leading-relaxed mb-6 text-lg font-light">{description}</p>
          
          <div className="inline-flex items-center gap-2 bg-black/40 border border-neutral-800/80 text-xs px-4 py-2 rounded-xl text-neutral-300 font-medium">
             <span className="opacity-50">Retrieved via:</span> {badge}
          </div>
       </div>
    </motion.div>
  );
}
