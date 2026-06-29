'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, FileQuestion } from 'lucide-react';

export function ActionItems() {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-stone-900">Needs Attention</h3>
        <button className="text-sm text-stone-500 hover:text-stone-900 transition-colors">Dismiss All</button>
      </div>

      <div className="space-y-3">
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-orange-50 border border-orange-100 p-4 rounded-2xl flex items-center justify-between group cursor-pointer hover:bg-orange-100/50 transition-colors"
        >
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-orange-600 shadow-sm border border-orange-100">
              <FileQuestion className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-medium text-orange-900">Missing Context</h4>
              <p className="text-sm text-orange-700">We noticed a new Telmisartan prescription, but no associated diagnosis. Why was this prescribed?</p>
            </div>
          </div>
          <button className="w-8 h-8 rounded-full bg-white flex items-center justify-center text-orange-600 shadow-sm border border-orange-100 group-hover:scale-110 transition-transform">
            <ArrowRight className="w-4 h-4" />
          </button>
        </motion.div>
      </div>
    </div>
  );
}
