"use client";

import React from "react";
import { motion } from "framer-motion";
import { Activity, ShieldCheck, Heart } from "lucide-react";

export function FamilyStatusBoard() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white p-5 rounded-2xl border border-stone-200 shadow-sm flex items-start gap-4"
      >
        <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <div>
          <h3 className="font-semibold text-stone-900">Stable</h3>
          <p className="text-sm text-stone-500 mt-1">
            No active escalations. The Smith family is healthy today.
          </p>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white p-5 rounded-2xl border border-stone-200 shadow-sm flex items-start gap-4"
      >
        <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
          <Activity className="w-6 h-6" />
        </div>
        <div>
          <h3 className="font-semibold text-stone-900">Recent Change</h3>
          <p className="text-sm text-stone-500 mt-1">
            John's hypertension medication was logged 2 days ago.
          </p>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white p-5 rounded-2xl border border-stone-200 shadow-sm flex items-start gap-4"
      >
        <div className="p-3 bg-rose-50 text-rose-600 rounded-xl">
          <Heart className="w-6 h-6" />
        </div>
        <div>
          <h3 className="font-semibold text-stone-900">Digital Twin</h3>
          <p className="text-sm text-stone-500 mt-1">
            Confidence score is high (92%). Memory is up to date.
          </p>
        </div>
      </motion.div>
    </div>
  );
}
