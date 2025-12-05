"use client";

import { motion } from "framer-motion";
import { AlertCircle, RotateCcw } from "lucide-react";

interface ErrorStateProps {
    message?: string | null;
    onRetry: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-md mx-auto p-6 rounded-xl border border-red-200 bg-red-50 text-center space-y-4"
        >
            <div className="mx-auto w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-red-600" />
            </div>

            <div className="space-y-1">
                <h3 className="font-semibold text-red-900">Algo salió mal</h3>
                <p className="text-sm text-red-700">
                    {message || "Ocurrió un error inesperado al procesar tu solicitud."}
                </p>
            </div>

            <button
                onClick={onRetry}
                className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-white border border-red-200 text-red-700 font-medium hover:bg-red-50 transition-colors shadow-sm"
            >
                <RotateCcw className="w-4 h-4" />
                Intentar de nuevo
            </button>
        </motion.div>
    );
}
