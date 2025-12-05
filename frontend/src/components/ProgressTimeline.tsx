"use client";

import { motion } from "framer-motion";
import { Check, Circle, Loader2 } from "lucide-react";
import clsx from "clsx";
import { JobStatus } from "../types";

interface ProgressTimelineProps {
    status: JobStatus;
}

const STEPS: { id: JobStatus; label: string }[] = [
    { id: "QUEUED", label: "En cola de espera..." },
    { id: "PROCESSING_IMAGES", label: "Procesando imágenes..." },
    { id: "GENERATING_STORY", label: "Generando historia..." },
    { id: "GENERATING_IMAGE", label: "Generando panel final..." },
    { id: "UPLOADING", label: "Finalizando..." },
];

export function ProgressTimeline({ status }: ProgressTimelineProps) {
    const currentIndex = STEPS.findIndex((s) => s.id === status);
    // If status is not in STEPS (e.g. COMPLETED or FAILED), handle gracefully
    // COMPLETED means all done. FAILED means stopped.

    const isCompleted = status === "COMPLETED";

    return (
        <div className="w-full max-w-sm mx-auto py-8">
            <div className="relative space-y-8">
                {/* Vertical Line */}
                <div className="absolute left-3 top-2 bottom-2 w-px bg-zinc-200 -z-10" />

                {STEPS.map((step, index) => {
                    let state: "upcoming" | "current" | "completed" = "upcoming";

                    if (isCompleted) {
                        state = "completed";
                    } else if (currentIndex > index) {
                        state = "completed";
                    } else if (currentIndex === index) {
                        state = "current";
                    }

                    return (
                        <div key={step.id} className="flex items-center gap-4">
                            <div
                                className={clsx(
                                    "relative flex items-center justify-center w-6 h-6 rounded-full border-2 transition-colors duration-300 bg-white",
                                    state === "completed" && "border-zinc-900 bg-zinc-900 text-white",
                                    state === "current" && "border-zinc-900",
                                    state === "upcoming" && "border-zinc-200"
                                )}
                            >
                                {state === "completed" && <Check className="w-3 h-3" />}
                                {state === "current" && (
                                    <motion.div
                                        layoutId="current-step-indicator"
                                        className="absolute inset-0 rounded-full border-2 border-zinc-900"
                                        animate={{ scale: [1, 1.2, 1], opacity: [1, 0.5, 1] }}
                                        transition={{ repeat: Infinity, duration: 2 }}
                                    />
                                )}
                                {state === "current" && <div className="w-2 h-2 rounded-full bg-zinc-900" />}
                            </div>
                            <span
                                className={clsx(
                                    "text-sm font-medium transition-colors duration-300",
                                    state === "current" ? "text-zinc-900" : "text-zinc-400"
                                )}
                            >
                                {step.label}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
