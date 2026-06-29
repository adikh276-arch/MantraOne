"use client";

import { useState, useEffect } from "react";
import { Scene1Welcome } from "@/features/demo/components/Scene1Welcome";
import { Scene2Upload } from "@/features/demo/components/Scene2Upload";
import { Scene3Graph } from "@/features/demo/components/Scene3Graph";
import { Scene4Retrieval } from "@/features/demo/components/Scene4Retrieval";
import { Scene5Timeline } from "@/features/demo/components/Scene5Timeline";
import { Scene6Escalation } from "@/features/demo/components/Scene6Escalation";

type DemoStep =
  "welcome" | "upload" | "graph" | "chat" | "timeline" | "escalation";

export default function DemoPage() {
  const [step, setStep] = useState<DemoStep>("welcome");

  // Use suspense or simple searchParams in a client component? Next 15 requires useSearchParams
  // Since we don't have suspense boundary here easily, we can just grab it from window.location if we are client side
  const [mode, setMode] = useState<"live" | "presentation">("presentation");

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("mode") === "live") {
      setMode("live");
    }
  }, []);

  const renderStep = () => {
    switch (step) {
      case "welcome":
        return <Scene1Welcome onNext={() => setStep("upload")} />;
      case "upload":
        return <Scene2Upload onNext={() => setStep("graph")} mode={mode} />;
      case "graph":
        return <Scene3Graph onNext={() => setStep("chat")} mode={mode} />;
      case "chat":
        return (
          <Scene4Retrieval onNext={() => setStep("timeline")} mode={mode} />
        );
      case "timeline":
        return (
          <Scene5Timeline onNext={() => setStep("escalation")} mode={mode} />
        );
      case "escalation":
        return (
          <Scene6Escalation onRestart={() => setStep("welcome")} mode={mode} />
        );
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 font-sans selection:bg-neutral-800 selection:text-white">
      {/* Navigation / Header */}
      <header className="fixed top-0 left-0 right-0 p-6 flex justify-between items-center z-50 mix-blend-difference pointer-events-none">
        <h1 className="text-xl font-medium tracking-tight">MantraOne</h1>
        <div className="flex flex-col items-end gap-1">
          <div className="text-sm font-medium opacity-50 uppercase tracking-widest">
            Demo: {step}
          </div>
          <div
            className={`text-xs font-mono px-2 py-0.5 rounded border ${mode === "live" ? "bg-red-500/20 text-red-400 border-red-500/30" : "bg-blue-500/20 text-blue-400 border-blue-500/30"}`}
          >
            {mode.toUpperCase()} MODE
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="relative min-h-screen w-full flex flex-col items-center justify-center overflow-x-hidden pt-24 pb-24">
        {renderStep()}
      </main>
    </div>
  );
}
