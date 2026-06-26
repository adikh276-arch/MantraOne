"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud, Activity, Database, CheckCircle, FileText, Send, Clock, User, HeartPulse } from "lucide-react";

type DemoStep = "landing" | "uploading" | "processing" | "memory_updated" | "chat" | "retrieving" | "answering" | "timeline" | "escalation";

export default function DemoPage() {
  const [step, setStep] = useState<DemoStep>("landing");

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 font-sans selection:bg-neutral-800 selection:text-white">
      {/* Navigation / Header */}
      <header className="fixed top-0 left-0 right-0 p-6 flex justify-between items-center z-50 mix-blend-difference">
        <h1 className="text-xl font-medium tracking-tight">MantraOne</h1>
        <div className="text-sm font-medium opacity-50 uppercase tracking-widest">
          {step.replace("_", " ")}
        </div>
      </header>

      {/* Main Content Area */}
      <main className="relative h-screen w-full flex flex-col items-center justify-center overflow-hidden">
        
        <AnimatePresence mode="wait">
          {step === "landing" && (
            <motion.div 
              key="landing"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="text-center max-w-2xl px-6"
            >
              <h2 className="text-5xl font-semibold tracking-tighter mb-6">
                Meet the Sharma Family
              </h2>
              <p className="text-neutral-400 text-lg mb-12">
                Healthcare usually starts from zero. MantraOne remembers everything. Watch how it works.
              </p>
              <button 
                onClick={() => setStep("uploading")}
                className="bg-white text-black px-8 py-4 rounded-full font-medium hover:scale-105 transition-transform"
              >
                Upload Dad's Diabetes Report
              </button>
            </motion.div>
          )}

          {step === "uploading" && (
            <motion.div 
              key="uploading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center"
            >
              <UploadCloud className="w-16 h-16 mb-6 text-blue-500 animate-bounce" />
              <h3 className="text-2xl font-medium">Uploading diabetes_lab.pdf</h3>
              <p className="text-neutral-500 mt-2">Securely transferring to MantraOne...</p>
              <button onClick={() => setStep("processing")} className="mt-8 text-sm underline opacity-50">Next: Processing</button>
            </motion.div>
          )}

          {step === "processing" && (
            <motion.div 
              key="processing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center"
            >
              <Activity className="w-16 h-16 mb-6 text-purple-500 animate-pulse" />
              <h3 className="text-2xl font-medium">Extracting Entities</h3>
              <p className="text-neutral-500 mt-2">Identifying HbA1c, Fasting Glucose, Metformin...</p>
              <button onClick={() => setStep("memory_updated")} className="mt-8 text-sm underline opacity-50">Next: Memory Update</button>
            </motion.div>
          )}

          {step === "memory_updated" && (
            <motion.div 
              key="memory_updated"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center"
            >
              <Database className="w-16 h-16 mb-6 text-green-500" />
              <h3 className="text-2xl font-medium">Living Memory Graph Updated</h3>
              
              {/* Dummy Graph Visual */}
              <div className="mt-12 relative w-[600px] h-[300px] border border-neutral-800 rounded-xl bg-neutral-900/50 flex items-center justify-center overflow-hidden">
                 <div className="absolute top-10 left-10 p-4 border border-blue-500/30 rounded-lg bg-blue-500/10 text-sm">Dad (Anil)</div>
                 <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 p-4 border border-purple-500/30 rounded-lg bg-purple-500/10 text-sm">Type 2 Diabetes</div>
                 <div className="absolute bottom-10 right-10 p-4 border border-red-500/30 rounded-lg bg-red-500/10 text-sm">HbA1c: 8.2%</div>
                 
                 {/* Edges */}
                 <svg className="absolute inset-0 w-full h-full -z-10 opacity-30">
                   <line x1="100" y1="80" x2="300" y2="150" stroke="currentColor" strokeWidth="2" strokeDasharray="4 4" />
                   <line x1="300" y1="150" x2="500" y2="250" stroke="currentColor" strokeWidth="2" strokeDasharray="4 4" />
                 </svg>
              </div>

              <button onClick={() => setStep("chat")} className="mt-12 bg-white text-black px-8 py-3 rounded-full font-medium">
                Continue to Chat
              </button>
            </motion.div>
          )}

          {step === "chat" && (
            <motion.div 
              key="chat"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="w-full max-w-3xl flex flex-col items-center"
            >
              <div className="w-full p-6 border border-neutral-800 rounded-2xl bg-neutral-900/40 backdrop-blur-sm mb-6">
                 <p className="text-lg">What has changed in Dad's health recently?</p>
              </div>
              
              <button 
                onClick={() => setStep("retrieving")}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl transition-colors"
              >
                <Send className="w-4 h-4" /> Ask MantraOne
              </button>
            </motion.div>
          )}

          {step === "retrieving" && (
            <motion.div 
              key="retrieving"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="w-full max-w-3xl"
            >
              <h3 className="text-xl font-medium mb-8 text-center text-neutral-400">Retrieving Family Memory...</h3>
              
              <div className="space-y-4">
                <motion.div initial={{ x: -20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 0.2 }} className="flex items-center gap-4 p-4 border border-neutral-800 rounded-xl bg-neutral-900">
                  <CheckCircle className="text-green-500 w-5 h-5" /> Found: Diabetes Lab Report (Oct 15)
                </motion.div>
                <motion.div initial={{ x: -20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 0.6 }} className="flex items-center gap-4 p-4 border border-neutral-800 rounded-xl bg-neutral-900">
                  <CheckCircle className="text-green-500 w-5 h-5" /> Found: Previous Consultation (Sep 02)
                </motion.div>
                <motion.div initial={{ x: -20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 1.0 }} className="flex items-center gap-4 p-4 border border-neutral-800 rounded-xl bg-neutral-900">
                  <CheckCircle className="text-green-500 w-5 h-5" /> Found: Timeline Events (Last 30 Days)
                </motion.div>
              </div>

              <div className="mt-12 flex justify-center">
                 <button onClick={() => setStep("answering")} className="text-sm underline opacity-50">Simulate Response</button>
              </div>
            </motion.div>
          )}

          {step === "answering" && (
            <motion.div 
              key="answering"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="w-full max-w-3xl p-8 border border-neutral-800 rounded-2xl bg-neutral-900/80"
            >
              <div className="flex items-center gap-4 mb-6 pb-6 border-b border-neutral-800">
                <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center">AI</div>
                <h4 className="font-medium">MantraOne</h4>
              </div>
              <p className="text-lg leading-relaxed text-neutral-300">
                Based on the recent lab report from October 15, Anil's HbA1c has risen to 8.2% and his fasting glucose is 165 mg/dL. The doctor has prescribed Metformin 500mg. 
                <br/><br/>
                This is a significant change from his previous consultation where his levels were stable. I've noted this in the timeline and will monitor his medication adherence.
              </p>
              
              <div className="mt-8 flex justify-end">
                 <button onClick={() => setStep("timeline")} className="text-sm bg-white text-black px-4 py-2 rounded-lg font-medium">View Timeline</button>
              </div>
            </motion.div>
          )}

          {step === "timeline" && (
            <motion.div 
              key="timeline"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="w-full max-w-4xl"
            >
              <h2 className="text-3xl font-medium mb-12 text-center">Family Health Timeline</h2>
              
              <div className="relative border-l border-neutral-800 ml-6 space-y-12 pb-12">
                 <div className="relative pl-8">
                    <div className="absolute w-4 h-4 rounded-full bg-blue-500 -left-[9px] top-1"></div>
                    <p className="text-sm text-blue-400 mb-1">Today</p>
                    <h4 className="text-xl font-medium">HbA1c Elevated to 8.2%</h4>
                    <p className="text-neutral-500 mt-2">New diagnosis of uncontrolled Type 2 Diabetes based on recent lab report.</p>
                 </div>
                 
                 <div className="relative pl-8 opacity-60">
                    <div className="absolute w-4 h-4 rounded-full bg-neutral-600 -left-[9px] top-1"></div>
                    <p className="text-sm text-neutral-400 mb-1">Sep 02</p>
                    <h4 className="text-xl font-medium">Routine Checkup</h4>
                    <p className="text-neutral-500 mt-2">All vitals stable. No medication changes.</p>
                 </div>
              </div>

              <div className="flex justify-center mt-8">
                <button onClick={() => setStep("escalation")} className="bg-red-600/20 text-red-500 border border-red-600/50 hover:bg-red-600/30 px-6 py-3 rounded-full font-medium transition-colors">
                  Trigger Escalation Demo
                </button>
              </div>
            </motion.div>
          )}

          {step === "escalation" && (
            <motion.div 
              key="escalation"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="w-full max-w-3xl"
            >
              <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-8">
                <div className="flex items-center gap-4 mb-6 text-red-400">
                   <HeartPulse className="w-8 h-8 animate-pulse" />
                   <h2 className="text-2xl font-medium">Doctor Consultation Brief Generated</h2>
                </div>
                
                <div className="bg-black/50 p-6 rounded-xl font-mono text-sm text-neutral-300 space-y-4">
                  <p><span className="text-neutral-500">PATIENT:</span> Anil Sharma (52)</p>
                  <p><span className="text-neutral-500">REASON:</span> High HbA1c (8.2%) detected in routine labs.</p>
                  <p><span className="text-neutral-500">CONTEXT:</span> Patient's last HbA1c was 6.8%. Fasting glucose is 165 mg/dL. Currently experiencing fatigue.</p>
                  <p><span className="text-neutral-500">AI RECOMMENDATION:</span> Expedite endocrinologist review for Metformin initiation.</p>
                </div>
              </div>

              <div className="mt-12 text-center text-neutral-500 flex flex-col items-center gap-4">
                 <p>This is what proactive family healthcare looks like.</p>
                 <button onClick={() => setStep("landing")} className="text-sm underline opacity-50">Restart Demo</button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
