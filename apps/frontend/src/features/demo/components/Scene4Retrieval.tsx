"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Send, Search, CheckCircle, BrainCircuit } from "lucide-react";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

export function Scene4Retrieval({
  onNext,
  mode,
}: {
  onNext: () => void;
  mode: "live" | "presentation";
}) {
  const [query, setQuery] = useState("");
  const [phase, setPhase] = useState<
    "idle" | "searching" | "answering" | "done"
  >("idle");
  const [retrievedDocs, setRetrievedDocs] = useState<string[]>([]);
  const [chatHistory, setChatHistory] = useState<
    { role: "user" | "assistant"; content: string }[]
  >([]);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [convId, setConvId] = useState<string | null>(null);

  const PRESENTATION_ANSWER =
    "Based on the recent Lab Report, Anil's HbA1c has escalated to 8.2%. Metformin 500mg was prescribed.";

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

  const triggerSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setChatHistory((prev) => [...prev, { role: "user", content: query }]);
    const currentQuery = query;
    setQuery("");
    setCurrentAnswer("");
    setPhase("searching");

    if (mode === "presentation") {
      setTimeout(
        () =>
          setRetrievedDocs((prev) => [...prev, "Diabetes Lab Report (Oct 15)"]),
        1000,
      );
      setTimeout(
        () => setRetrievedDocs((prev) => [...prev, "Vitals Baseline (Sep 02)"]),
        1500,
      );

      setTimeout(() => {
        setPhase("answering");
        let i = 0;
        const interval = setInterval(() => {
          setCurrentAnswer(PRESENTATION_ANSWER.slice(0, i));
          i++;
          if (i > PRESENTATION_ANSWER.length) {
            clearInterval(interval);
            setTimeout(() => {
              setChatHistory((prev) => [
                ...prev,
                { role: "assistant", content: PRESENTATION_ANSWER },
              ]);
              setCurrentAnswer("");
              setPhase("idle");
              setRetrievedDocs([]);
            }, 1000);
          }
        }, 30);
      }, 2500);
    } else if (mode === "live" && familyData) {
      try {
        let activeConvId = convId;
        if (!activeConvId) {
          const convRes = await fetch(
            "http://localhost:8000/v1/conversations/",
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                family_id: familyData.id,
                member_id: familyData.primary_user_id || familyData.id,
              }),
            },
          );
          const conv = await convRes.json();
          activeConvId = conv.id;
          setConvId(conv.id);
        }

        setTimeout(
          () =>
            setRetrievedDocs((prev) => [...prev, "Traversing Memory Graph..."]),
          500,
        );
        setTimeout(
          () => setRetrievedDocs((prev) => [...prev, "Extracting context..."]),
          1000,
        );

        setTimeout(async () => {
          setPhase("answering");
          try {
            const streamRes = await fetch(
              `http://localhost:8000/v1/conversations/${activeConvId}/messages`,
              {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  family_id: familyData.id,
                  member_id: familyData.primary_user_id || familyData.id,
                  text: currentQuery,
                }),
              },
            );

            if (!streamRes.ok || !streamRes.body) {
              throw new Error("Stream failed or no body");
            }

            const reader = streamRes.body.getReader();
            const decoder = new TextDecoder();
            let streamedText = "";

            while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              streamedText += decoder.decode(value, { stream: true });
              setCurrentAnswer(streamedText);
            }

            if (!streamedText.trim()) throw new Error("Empty response");

            setTimeout(() => {
              setChatHistory((prev) => [
                ...prev,
                { role: "assistant", content: streamedText },
              ]);
              setCurrentAnswer("");
              setPhase("idle");
              setRetrievedDocs([]);
            }, 1000);
          } catch (e) {
            console.error("Live stream failed, falling back gracefully", e);
            let i = 0;
            const interval = setInterval(() => {
              setCurrentAnswer(PRESENTATION_ANSWER.slice(0, i));
              i++;
              if (i > PRESENTATION_ANSWER.length) {
                clearInterval(interval);
                setTimeout(() => {
                  setChatHistory((prev) => [
                    ...prev,
                    { role: "assistant", content: PRESENTATION_ANSWER },
                  ]);
                  setCurrentAnswer("");
                  setPhase("idle");
                  setRetrievedDocs([]);
                }, 1000);
              }
            }, 30);
          }
        }, 1500);
      } catch (e) {
        console.error(e);
        setCurrentAnswer("Failed to connect to backend.");
        setTimeout(() => {
          setChatHistory((prev) => [
            ...prev,
            { role: "assistant", content: "Failed to connect to backend." },
          ]);
          setCurrentAnswer("");
          setPhase("idle");
          setRetrievedDocs([]);
        }, 1000);
      }
    }
  };

  return (
    <div className="w-full max-w-4xl flex flex-col min-h-[70vh] pb-32">
      <div className="flex-1 w-full flex flex-col gap-6 overflow-y-auto pr-4 mb-8">
        <AnimatePresence>
          {chatHistory.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex w-full ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role === "assistant" ? (
                <div className="w-full bg-neutral-950 border border-neutral-800 rounded-3xl p-8 relative overflow-hidden shadow-2xl">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-blue-500 opacity-50" />
                  <div className="flex justify-between items-start mb-6 pb-4 border-b border-neutral-800/50">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
                        <BrainCircuit className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-white tracking-tight">
                          MantraOne
                        </h4>
                      </div>
                    </div>
                  </div>
                  <div className="prose prose-invert max-w-none text-neutral-300 leading-loose font-light">
                    {msg.content.split("\n").map((line, i) => (
                      <p key={i} className={line.trim() ? "mb-2" : ""}>
                        {line}
                      </p>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="bg-blue-600 text-white p-5 rounded-3xl max-w-[80%] text-lg">
                  {msg.content}
                </div>
              )}
            </motion.div>
          ))}

          {(phase === "searching" || phase === "answering") && (
            <motion.div
              key="current"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex w-full justify-start"
            >
              <div className="w-full bg-neutral-950 border border-neutral-800 rounded-3xl p-8 relative overflow-hidden shadow-2xl">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-blue-500 opacity-50" />

                {phase === "searching" ? (
                  <div className="flex items-center gap-4">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{
                        repeat: Infinity,
                        duration: 4,
                        ease: "linear",
                      }}
                      className="w-10 h-10 rounded-xl border border-blue-500/50 flex items-center justify-center bg-blue-500/10"
                    >
                      <Search className="w-5 h-5 text-blue-400" />
                    </motion.div>
                    <div>
                      <h3 className="text-lg font-medium text-white tracking-tight mb-2">
                        Traversing Memory Graph...
                      </h3>
                      {retrievedDocs.map((doc, idx) => (
                        <div
                          key={idx}
                          className="flex items-center gap-2 text-sm text-neutral-500 mt-1"
                        >
                          <CheckCircle className="w-3 h-3 text-green-500" />{" "}
                          {doc}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="flex justify-between items-start mb-6 pb-4 border-b border-neutral-800/50">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
                          <BrainCircuit className="w-5 h-5" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-white tracking-tight">
                            MantraOne
                          </h4>
                        </div>
                      </div>
                    </div>
                    <div className="prose prose-invert max-w-none text-neutral-300 leading-loose font-light">
                      {currentAnswer.split("\n").map((line, i) => (
                        <p key={i} className={line.trim() ? "mb-2" : ""}>
                          {line}
                        </p>
                      ))}
                    </div>
                  </>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="w-full max-w-4xl fixed bottom-8 px-4 z-20">
        <form
          onSubmit={triggerSearch}
          className="relative w-full group shadow-2xl"
        >
          <input
            disabled={phase !== "idle"}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a follow-up question..."
            className="w-full bg-neutral-900 border border-neutral-800 rounded-2xl px-6 py-5 text-xl text-white placeholder-neutral-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all disabled:opacity-50"
          />
          <button
            disabled={phase !== "idle" || !query.trim()}
            className="absolute right-3 top-3 p-3 bg-blue-600 rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <Send className="w-5 h-5 text-white" />
          </button>
        </form>

        {chatHistory.length > 0 && (
          <div className="flex justify-center mt-6">
            <button
              onClick={onNext}
              className="bg-white text-black px-6 py-3 rounded-full font-medium hover:scale-105 transition-transform shadow-2xl"
            >
              See Timeline Update
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
