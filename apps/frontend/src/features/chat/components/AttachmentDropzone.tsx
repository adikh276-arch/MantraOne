"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud } from "lucide-react";

interface AttachmentDropzoneProps {
  children: React.ReactNode;
}

export function AttachmentDropzone({ children }: AttachmentDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      console.log("File dropped:", files[0].name);
      // Initiate upload mutation and OCR pipeline
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className="relative"
    >
      <AnimatePresence>
        {isDragging && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-50 bg-stone-900/10 backdrop-blur-sm rounded-b-2xl border-2 border-dashed border-stone-400 flex flex-col items-center justify-center text-stone-600"
          >
            <UploadCloud className="w-10 h-10 mb-2" />
            <p className="font-medium">Drop report to analyze</p>
          </motion.div>
        )}
      </AnimatePresence>
      {children}
    </div>
  );
}
