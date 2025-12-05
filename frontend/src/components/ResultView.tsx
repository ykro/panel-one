"use client";

import { motion } from "framer-motion";
import { Download, RotateCcw } from "lucide-react";

interface ResultViewProps {
    resultUrl: string;
    onRestart: () => void;
}

export function ResultView({ resultUrl, onRestart }: ResultViewProps) {
    const handleDownload = async () => {
        try {
            const response = await fetch(`/api/proxy-image?url=${encodeURIComponent(resultUrl)}`);
            if (!response.ok) throw new Error("Download failed");

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = "panel-one-result.png"; // Or derive filename
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        } catch (e) {
            console.error("Download error:", e);
            // Fallback: open in new tab
            window.open(resultUrl, "_blank");
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-4xl mx-auto space-y-6"
        >
            <div className="relative aspect-video w-full rounded-2xl overflow-hidden shadow-2xl bg-white border border-zinc-200">
                <img
                    src={resultUrl}
                    alt="Generated Comic Panel"
                    className="w-full h-full object-contain" // Contain to ensure full image visible within 16:9
                />
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                    onClick={handleDownload}
                    className="flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-zinc-900 text-white font-medium hover:bg-zinc-800 transition-colors"
                >
                    <Download className="w-5 h-5" />
                    Descargar Panel
                </button>
                <button
                    onClick={onRestart}
                    className="flex items-center justify-center gap-2 px-6 py-3 rounded-lg border border-zinc-200 bg-white text-zinc-900 font-medium hover:bg-zinc-50 transition-colors"
                >
                    <RotateCcw className="w-5 h-5" />
                    Crear Nuevo
                </button>
            </div>
        </motion.div>
    );
}
