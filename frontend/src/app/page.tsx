"use client";

import { usePanelGenerator } from "@/hooks/usePanelGenerator";
import { UploadZone } from "@/components/UploadZone";
import { ProgressTimeline } from "@/components/ProgressTimeline";
import { ResultView } from "@/components/ResultView";
import { ErrorState } from "@/components/ErrorState";
import { Toaster } from "sonner";
import { motion, AnimatePresence } from "framer-motion";

export default function Home() {
  const { status, resultUrl, error, startJob, reset } = usePanelGenerator();

  // Determine current view
  const renderContent = () => {
    if (status === "COMPLETED" && resultUrl) {
      return (
        <ResultView resultUrl={resultUrl} onRestart={reset} />
      );
    }

    if (status === "FAILED" || error) {
      return (
        <ErrorState message={error} onRetry={reset} />
      );
    }

    if (status) {
      return <ProgressTimeline status={status} />;
    }

    return (
      <UploadZone
        onStart={startJob}
        isLoading={false} // Loading handled by status transition
      />
    );
  };

  return (
    <main className="min-h-screen bg-zinc-50 py-12 px-4 sm:px-6">
      <div className="max-w-7xl mx-auto space-y-12">
        <header className="text-center space-y-4">
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-zinc-900">
            Panel One
          </h1>
          <p className="text-lg text-zinc-500 max-w-2xl mx-auto">
            Transforma tus fotos en una historia única al estilo cómic.
          </p>
        </header>

        <div className="flex justify-center">
          <AnimatePresence mode="wait">
            <motion.div
              key={status || "upload"}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="w-full"
            >
              {renderContent()}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
      <Toaster position="bottom-center" />
    </main>
  );
}
