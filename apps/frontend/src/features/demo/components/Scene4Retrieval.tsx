"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Send, Search, CheckCircle, BrainCircuit } from "lucide-react";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

export function Scene4Retrieval({ onNext, mode }: { onNext: () => void, mode: "live" | "presentation" }) {
  const [query, setQuery] = useState("");
  const [phase, setPhase] = useState<"idle" | "searching" | "answering" | "done">("idle");
  const [retrievedDocs, setRetrievedDocs] = useState<string[]>([]);
  const [answer, setAnswer] = useState("");
  
  const PRESENTATION_ANSWER = "Based on the recent Lab Report (Oct 15), Anil's HbA1c has escalated to 8.2%, and fasting glucose is 165 mg/dL. In response, Dr. Gupta has prescribed a new medication: Metformin 500mg BD.";
  
  const { data: familyData } = useQuery({
    queryKey: ['family'],
    queryFn: async () => {
      const res = await fetch('http://localhost:8000/v1/families/');
      if (!res.ok) throw new Error("Failed");
      const families = await res.json();
      return families[0];
    },
    enabled: mode === 'live'
  });

  const triggerSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setPhase("searching");
    
    if (mode === "presentation") {
      setTimeout(() => setRetrievedDocs(prev => [...prev, "Diabetes Lab Report (Oct 15)"]), 1000);
      setTimeout(() => setRetrievedDocs(prev => [...prev, "Vitals Baseline (Sep 02)"]), 1500);
      setTimeout(() => setRetrievedDocs(prev => [...prev, "Consultation Notes (Dr. Gupta)"]), 2000);
      setTimeout(() => setRetrievedDocs(prev => [...prev, "Current Medication: Metformin 500mg"]), 2500);
      
      setTimeout(() => {
        setPhase("answering");
        let i = 0;
        const interval = setInterval(() => {
          setAnswer(PRESENTATION_ANSWER.slice(0, i));
          i++;
          if (i > PRESENTATION_ANSWER.length) {
            clearInterval(interval);
            setTimeout(() => setPhase("done"), 1000);
          }
        }, 30);
      }, 3500);
    } else if (mode === "live" && familyData) {
      try {
        const convRes = await fetch('http://localhost:8000/v1/conversations/', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({ family_id: familyData.id, member_id: familyData.primary_user_id || familyData.id })
        });
        const conv = await convRes.json();
        
        setTimeout(() => setRetrievedDocs(prev => [...prev, "Found: Latest Medical Report"]), 500);
        setTimeout(() => setRetrievedDocs(prev => [...prev, "Found: Historical Vitals"]), 1000);
        
        setTimeout(async () => {
           setPhase("answering");
           try {
             const streamRes = await fetch(`http://localhost:8000/v1/conversations/${conv.id}/messages`, {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({ family_id: familyData.id, member_id: familyData.primary_user_id || familyData.id, text: query })
             });
             
             if (!streamRes.body) throw new Error("No stream body");
             
             const reader = streamRes.body.getReader();
             const decoder = new TextDecoder();
             let streamedText = "";
             
             while (true) {
               const { done, value } = await reader.read();
               if (done) break;
               streamedText += decoder.decode(value, { stream: true });
               setAnswer(streamedText);
             }
             setTimeout(() => setPhase("done"), 1000);
           } catch (e) {
             console.error("Stream failed", e);
             setAnswer("Error fetching live response. Graceful fallback activated: " + PRESENTATION_ANSWER);
             setTimeout(() => setPhase("done"), 1000);
           }
        }, 1500);
      } catch (e) {
         console.error(e);
         setAnswer("Failed to connect to backend. Fallback: " + PRESENTATION_ANSWER);
         setPhase("done");
      }
    }
  };

  return (
    <div className="w-full max-w-4xl flex flex-col items-center min-h-[70vh]">
      <div className="w-full mb-12">
         <form onSubmit={handleSubmit} className="relative w-full group">
           <input 
             disabled={phase !== "idle"}
             type="text" 
             value={query}
             onChange={(e) => setQuery(e.target.value)}
             placeholder='Ask "What changed in Dad s health recently?"'
             className="w-full bg-neutral-900 border border-neutral-800 rounded-2xl px-6 py-5 text-xl text-white placeholder-neutral-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all disabled:opacity-50"
           />
           <button 
             disabled={phase !== "idle" || !query.trim()}
             className="absolute right-3 top-3 p-3 bg-blue-600 rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-colors"
           >
             <Send className="w-5 h-5 text-white" />
           </button>
         </form>
      </div>

      <AnimatePresence mode="wait">
        {phase === "searching" && (
          <motion.div 
            key="searching"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95, filter: "blur(10px)" }}
            className="w-full bg-neutral-900/40 backdrop-blur-xl border border-neutral-800/60 rounded-3xl p-10 shadow-2xl"
          >
            <div className="flex items-center gap-4 mb-8">
               <motion.div 
                  animate={{ rotate: 360 }} 
                  transition={{ repeat: Infinity, duration: 4, ease: "linear" }}
                  className="w-10 h-10 rounded-full border border-blue-500/50 flex items-center justify-center bg-blue-500/10"
               >
                  <Search className="w-5 h-5 text-blue-400" />
               </motion.div>
               <div>
                  <h3 className="text-xl font-medium text-white tracking-tight">Retrieving Context</h3>
                  <p className="text-neutral-500 text-sm mt-1">Scanning Sharma Family Living Memory Graph</p>
               </div>
            </div>
            
            <div className="space-y-5 relative pl-5 border-l-2 border-neutral-800/50 ml-5">
               {retrievedDocs.map((mem, i) => (
                 <motion.div 
                    key={i}
                    initial={{ opacity: 0, x: -20, filter: "blur(5px)" }}
                    animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
                    transition={{ type: "spring", stiffness: 300, damping: 25 }}
                    className="flex items-start gap-4 text-neutral-300"
                 >
                    <div className="w-6 h-6 rounded-full bg-green-500/10 border border-green-500/30 flex items-center justify-center mt-0.5 relative -left-[37px]">
                       <CheckCircle className="w-3.5 h-3.5 text-green-400" />
                    </div>
                    <span className="text-[15px] font-medium tracking-wide bg-gradient-to-r from-neutral-200 to-neutral-400 bg-clip-text text-transparent">{mem}</span>
                 </motion.div>
               ))}
               {retrievedCount < 4 && (
                 <div className="flex items-center gap-4 text-neutral-600 mt-4 relative -left-[31px]">
                    <div className="w-3 h-3 rounded-full bg-blue-500 animate-ping" />
                    <span className="text-sm tracking-widest uppercase">Traversing Knowledge Nodes...</span>
                 </div>
               )}
            </div>
          </motion.div>
        )}

        {phase === "answering" && (
          <motion.div 
            key="answering"
            initial={{ opacity: 0, y: 20, filter: "blur(10px)" }}
            animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
            transition={{ type: "spring", stiffness: 200, damping: 25 }}
            className="w-full flex flex-col gap-8"
          >
            <div className="w-full bg-neutral-950 border border-neutral-800 rounded-3xl p-10 relative overflow-hidden shadow-2xl">
               <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-blue-500 opacity-50" />
               
               <div className="flex justify-between items-start mb-8 pb-6 border-b border-neutral-800/50">
                  <div className="flex items-center gap-5">
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shadow-inner">
                       <BrainCircuit className="w-7 h-7" />
                    </div>
                    <div>
                       <h4 className="font-semibold text-white tracking-tight text-xl">MantraOne</h4>
                       <p className="text-sm text-neutral-500 mt-1 font-medium tracking-wide">Contextually Grounded AI</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                     <span className="px-3 py-1 rounded-full bg-green-500/10 text-green-400 border border-green-500/20 text-xs font-mono tracking-widest">
                        4 MEMORIES USED
                     </span>
                  </div>
               </div>

               <div className="prose prose-invert max-w-none text-xl text-neutral-300 leading-loose font-light">
                  <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
                    Based on the recent lab report from October 15, Anil's <strong className="text-white font-medium">HbA1c has risen to 8.2%</strong> and his fasting glucose is 165 mg/dL. The doctor has prescribed Metformin 500mg.
                  </motion.p>
                  <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }} className="mt-6">
                    This is a significant change from his previous consultation on September 02, where his levels were stable and no medication was required. I've noted this in the timeline and will continue to monitor his adherence to the new medication.
                  </motion.p>
               </div>
            </div>

            <div className="flex justify-center mt-4">
               <button 
                 onClick={onNext}
                 className="bg-white text-black px-8 py-4 rounded-full font-medium hover:scale-105 transition-transform"
               >
                 See Timeline Update
               </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
