'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useOnboardingStore } from '../store';
import { ArrowRight, Users, FileText } from 'lucide-react';

export function OnboardingFlow() {
  const { step, setStep } = useOnboardingStore();

  const renderStep = () => {
    switch (step) {
      case 'welcome':
        return (
          <motion.div
            key="welcome"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="flex flex-col items-center justify-center text-center space-y-6 max-w-md mx-auto h-full"
          >
            <div className="w-16 h-16 bg-stone-900 rounded-2xl flex items-center justify-center shadow-lg mb-4">
              <span className="text-white font-semibold text-xl">M1</span>
            </div>
            <h1 className="text-3xl font-semibold tracking-tight text-stone-900">Meet MantraOne.</h1>
            <p className="text-stone-500 leading-relaxed">
              Your family's intelligent health companion. Let's create your digital twin so we can keep track of what matters.
            </p>
            <button
              onClick={() => setStep('create_family')}
              className="mt-8 flex items-center gap-2 bg-stone-900 text-white px-6 py-3 rounded-full hover:bg-stone-800 transition-colors shadow-sm"
            >
              Start Building <ArrowRight className="w-4 h-4" />
            </button>
          </motion.div>
        );

      case 'create_family':
        return (
          <motion.div
            key="create_family"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="flex flex-col items-center justify-center space-y-8 max-w-md mx-auto h-full w-full"
          >
            <div className="text-center space-y-2">
              <Users className="w-8 h-8 text-stone-900 mx-auto mb-4" />
              <h2 className="text-2xl font-semibold text-stone-900">Who are we caring for?</h2>
            </div>
            
            <div className="w-full space-y-4">
              <input
                type="text"
                placeholder="Family Name (e.g. The Smiths)"
                className="w-full bg-white border border-stone-200 rounded-xl px-4 py-4 text-stone-800 focus:outline-none focus:ring-2 focus:ring-stone-900 transition-shadow"
              />
              <button
                onClick={() => setStep('upload_reports')}
                className="w-full bg-stone-900 text-white px-6 py-4 rounded-xl hover:bg-stone-800 transition-colors shadow-sm font-medium"
              >
                Continue
              </button>
            </div>
          </motion.div>
        );

      case 'upload_reports':
        return (
          <motion.div
            key="upload"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="flex flex-col items-center justify-center space-y-8 max-w-md mx-auto h-full w-full"
          >
            <div className="text-center space-y-2">
              <FileText className="w-8 h-8 text-stone-900 mx-auto mb-4" />
              <h2 className="text-2xl font-semibold text-stone-900">Add medical context</h2>
              <p className="text-stone-500 text-sm">Upload past lab reports or prescriptions to jumpstart the Digital Twin.</p>
            </div>
            
            <div className="w-full aspect-video border-2 border-dashed border-stone-300 rounded-2xl flex flex-col items-center justify-center text-stone-500 hover:border-stone-900 hover:text-stone-900 transition-colors cursor-pointer bg-stone-50">
              <span>Drop a PDF here</span>
            </div>
            
            <button
              onClick={() => setStep('first_conversation')}
              className="w-full bg-stone-900 text-white px-6 py-4 rounded-xl hover:bg-stone-800 transition-colors shadow-sm font-medium"
            >
              Start Chatting
            </button>
          </motion.div>
        );

      case 'first_conversation':
        return (
          <motion.div
            key="first_conv"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="h-full flex items-center justify-center text-stone-500"
          >
            Redirecting to Chat...
          </motion.div>
        );
    }
  };

  return (
    <div className="h-screen w-full bg-stone-100 flex items-center justify-center p-6">
      <div className="bg-white rounded-3xl shadow-sm border border-stone-200 w-full max-w-2xl h-[600px] overflow-hidden p-8 relative">
        <AnimatePresence mode="wait">
          {renderStep()}
        </AnimatePresence>
      </div>
    </div>
  );
}
