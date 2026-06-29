"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useSendMessage } from "../shared/api";
import { MessageRenderer } from "./MessageRenderer";
import { VoiceRecorder } from "./VoiceRecorder";
import { AttachmentDropzone } from "./AttachmentDropzone";
import { Loader2, Paperclip, Send } from "lucide-react";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  status: "sending" | "sent" | "error";
  attachments?: any[];
}

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  const sendMessageMutation = useSendMessage();

  const scrollToBottom = () => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      status: "sending",
    };

    setMessages((prev) => [...prev, newMessage]);
    setInput("");

    try {
      // Hardcoding family_id and member_id for demo. In a real app, grab from context.
      const res = await sendMessageMutation.mutateAsync({
        family_id: "fam_123",
        member_id: "mem_123",
        message: newMessage.content,
      });

      setMessages((prev) =>
        prev.map((m) =>
          m.id === newMessage.id ? { ...m, status: "sent" } : m,
        ),
      );

      setMessages((prev) => [
        ...prev,
        {
          id: res.message_id,
          role: "assistant",
          content: res.content,
          status: "sent",
        },
      ]);
    } catch (error) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === newMessage.id ? { ...m, status: "error" } : m,
        ),
      );
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-3xl mx-auto w-full bg-stone-50 rounded-2xl shadow-sm border border-stone-200 overflow-hidden relative">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <AnimatePresence>
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="h-full flex flex-col items-center justify-center text-stone-400 space-y-4"
            >
              <p className="text-lg font-medium text-stone-600">
                How is your family today?
              </p>
              <p className="text-sm text-center max-w-xs">
                Upload a report, record a voice memo, or just say hello to get
                started.
              </p>
            </motion.div>
          )}

          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              layout
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-5 py-3 ${
                  msg.role === "user"
                    ? "bg-stone-800 text-stone-50 rounded-br-sm"
                    : "bg-white text-stone-800 border border-stone-200 rounded-bl-sm shadow-sm"
                }`}
              >
                <MessageRenderer content={msg.content} />
                {msg.status === "sending" && (
                  <span className="inline-block ml-2 text-stone-400">
                    <Loader2 className="w-3 h-3 animate-spin inline" />
                  </span>
                )}
                {msg.status === "error" && (
                  <span className="block mt-1 text-xs text-red-400">
                    Failed to send. Click to retry.
                  </span>
                )}
              </div>
            </motion.div>
          ))}

          {sendMessageMutation.isPending && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="bg-white border border-stone-200 rounded-2xl rounded-bl-sm px-5 py-3 shadow-sm flex items-center space-x-1">
                <div className="w-2 h-2 bg-stone-300 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <div className="w-2 h-2 bg-stone-300 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <div className="w-2 h-2 bg-stone-300 rounded-full animate-bounce" />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={bottomRef} />
      </div>

      {/* Input Area */}
      <AttachmentDropzone>
        <div className="p-4 bg-white border-t border-stone-100 flex items-end gap-2">
          <button className="p-3 text-stone-400 hover:text-stone-600 transition-colors rounded-full hover:bg-stone-50">
            <Paperclip className="w-5 h-5" />
          </button>

          <div className="flex-1 bg-stone-50 border border-stone-200 rounded-2xl px-4 py-2 flex items-center focus-within:ring-2 focus-within:ring-stone-200 focus-within:border-transparent transition-all">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask about medications, symptoms, or upload a report..."
              className="w-full bg-transparent resize-none outline-none max-h-32 text-stone-700 py-1"
              rows={1}
            />
          </div>

          {input.trim() ? (
            <motion.button
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              onClick={handleSend}
              className="p-3 bg-stone-800 text-white rounded-full hover:bg-stone-700 transition-colors shadow-sm"
            >
              <Send className="w-5 h-5 ml-0.5" />
            </motion.button>
          ) : (
            <VoiceRecorder />
          )}
        </div>
      </AttachmentDropzone>
    </div>
  );
}
