"use client";

import { motion, AnimatePresence } from "framer-motion";
import {
  HeartPulse,
  Stethoscope,
  FileText,
  ArrowRight,
  AlertTriangle,
  Activity,
} from "lucide-react";
import { useState, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";

export function Scene6Escalation({
  onRestart,
  mode,
}: {
  onRestart: () => void;
  mode: "live" | "presentation";
}) {
  const [showBrief, setShowBrief] = useState(false);
  const [briefData, setBriefData] = useState<any>(null);

  const PRESENTATION_BRIEF = {
    brief:
      "Patient's HbA1c has sharply escalated to 8.2% (from 6.8% in previous checkup). Fasting glucose is currently 165 mg/dL. The patient reports worsening fatigue over the past 3 weeks.",
    reason:
      "Evaluate immediate initiation of Metformin 500mg. Review patient's lifestyle and stress factors (sleep data indicates reduced hours over the past week).",
  };

  const { data: familyData } = useQuery({
    queryKey: ["family"],
    queryFn: async () => {
      const res = await fetch("http://localhost:8000/v1/families/");
      if (!res.ok) throw new Error("Failed");
      const families = await res.json();
      return families[0];
    },
    enabled: mode === "live",
  });

  const escalationMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch("http://localhost:8000/v1/escalations/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          family_id: familyData.id,
          member_id: familyData.primary_user_id || familyData.id,
        }),
      });
      if (!res.ok) throw new Error("Failed");
      return await res.json();
    },
    onSuccess: (data) => {
      setBriefData(data);
    },
    onError: () => {
      setBriefData(PRESENTATION_BRIEF);
    },
  });

  useEffect(() => {
    let t1: NodeJS.Timeout, t2: NodeJS.Timeout;

    if (mode === "presentation") {
      t1 = setTimeout(() => {
        setShowBrief(true);
        setBriefData(PRESENTATION_BRIEF);
      }, 3000);
    } else if (mode === "live" && familyData) {
      t1 = setTimeout(() => {
        escalationMutation.mutate();
        t2 = setTimeout(() => {
          setShowBrief(true);
        }, 1500);
      }, 1500);
    }

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [mode, familyData]);

  return (
    <div className="w-full max-w-4xl flex flex-col items-center">
      {!showBrief && (
        <motion.div
          key="alerting"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 1.1, filter: "blur(10px)" }}
          className="flex flex-col items-center justify-center min-h-[50vh]"
        >
          <motion.div
            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
            transition={{ repeat: Infinity, duration: 1.5 }}
            className="w-32 h-32 bg-red-600/20 rounded-full flex items-center justify-center mb-8"
          >
            <div className="w-20 h-20 bg-red-600/40 rounded-full flex items-center justify-center backdrop-blur-sm">
              <AlertTriangle className="w-10 h-10 text-red-500" />
            </div>
          </motion.div>
          <h2 className="text-3xl font-medium text-white mb-3">
            Critical Escalation Triggered
          </h2>
          <p className="text-neutral-400 text-lg">
            System has detected a convergence of risk factors.
          </p>
        </motion.div>
      )}

      {showBrief && (
        <motion.div
          key="briefing"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full"
        >
          <div className="w-full flex items-center justify-between mb-8">
            <h2 className="text-3xl font-medium text-white flex items-center gap-3">
              <Stethoscope className="text-blue-500" /> Doctor Consultation
              Brief
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
                <p className="text-neutral-500 text-sm mb-2 uppercase tracking-widest font-mono">
                  Patient Profile
                </p>
                <p className="text-3xl text-white font-medium tracking-tight">
                  Anil Sharma{" "}
                  <span className="text-neutral-500 font-normal">
                    (52, Male)
                  </span>
                </p>
              </div>
              <div>
                <p className="text-neutral-500 text-sm mb-2 uppercase tracking-widest font-mono">
                  Primary Concern
                </p>
                <p className="text-2xl text-red-400 font-medium tracking-tight">
                  Uncontrolled Type 2 Diabetes
                </p>
              </div>
            </div>

            <div className="space-y-10">
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <h4 className="text-xl text-white font-medium mb-4 flex items-center gap-3">
                  <FileText className="w-5 h-5 text-neutral-500" /> AI Executive
                  Summary
                </h4>
                <div className="text-neutral-300 leading-relaxed text-lg bg-neutral-900/50 p-8 rounded-3xl border border-neutral-800/80 font-light">
                  {briefData?.brief || PRESENTATION_BRIEF.brief}
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.6 }}
                className="bg-blue-950/20 border border-blue-500/30 rounded-3xl p-8 mt-12 relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-transparent pointer-events-none" />
                <h4 className="text-blue-400 font-medium mb-3 text-lg">
                  Recommended Action for Doctor
                </h4>
                <p className="text-blue-200 leading-relaxed font-light text-lg">
                  {briefData?.reason || PRESENTATION_BRIEF.reason}
                </p>
              </motion.div>
            </div>
          </div>

          <div className="mt-16 flex flex-col items-center">
            <p className="text-neutral-500 text-lg mb-6 text-center max-w-lg">
              This is what proactive family healthcare looks like. MantraOne
              doesn't just remember—it acts.
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
