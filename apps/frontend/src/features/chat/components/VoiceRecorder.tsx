'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic } from 'lucide-react';

export function VoiceRecorder() {
  const [isRecording, setIsRecording] = useState(false);

  const handleHoldStart = () => setIsRecording(true);
  const handleHoldEnd = () => {
    setIsRecording(false);
    // Submit voice logic goes here
  };

  return (
    <div className="relative flex items-center">
      <AnimatePresence>
        {isRecording && (
          <motion.div
            initial={{ opacity: 0, width: 0 }}
            animate={{ opacity: 1, width: '160px' }}
            exit={{ opacity: 0, width: 0 }}
            className="absolute right-12 bg-red-50 text-red-600 rounded-full px-4 py-2 text-sm font-medium flex items-center overflow-hidden shadow-sm border border-red-100"
          >
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse mr-2" />
            Listening...
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        onPointerDown={handleHoldStart}
        onPointerUp={handleHoldEnd}
        onPointerLeave={handleHoldEnd}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className={`p-3 rounded-full transition-colors shadow-sm ${
          isRecording ? 'bg-red-500 text-white' : 'bg-stone-100 text-stone-600 hover:bg-stone-200'
        }`}
      >
        <Mic className="w-5 h-5" />
      </motion.button>
    </div>
  );
}
