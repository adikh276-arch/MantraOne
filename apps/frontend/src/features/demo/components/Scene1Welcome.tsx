"use client";

import { motion } from "framer-motion";

export function Scene1Welcome({ onNext }: { onNext: () => void }) {
  return (
    <motion.div
      key="landing"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="text-center max-w-3xl px-6 flex flex-col items-center justify-center min-h-[60vh]"
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.8, ease: "easeOut" }}
      >
        <h2 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6">
          Meet the Sharma Family
        </h2>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.8, ease: "easeOut" }}
      >
        <p className="text-neutral-400 text-xl md:text-2xl mb-12 font-light max-w-2xl leading-relaxed">
          Healthcare interactions usually start from zero. Every appointment is
          a reset.
          <span className="text-white block mt-4 font-normal">
            MantraOne remembers everything.
          </span>
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5, duration: 1 }}
      >
        <button
          onClick={onNext}
          className="bg-white text-black px-8 py-4 rounded-full font-medium hover:scale-105 transition-transform duration-300"
        >
          Begin the Demonstration
        </button>
      </motion.div>
    </motion.div>
  );
}
