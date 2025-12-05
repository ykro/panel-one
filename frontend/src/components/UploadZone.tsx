"use client";

import { useState, useCallback } from "react";
import { Upload, X, Image as ImageIcon } from "lucide-react";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import clsx from "clsx";

interface UploadZoneProps {
    onStart: (files: File[]) => void;
    isLoading: boolean;
}

export function UploadZone({ onStart, isLoading }: UploadZoneProps) {
    const [files, setFiles] = useState<File[]>([]);
    const [isDragging, setIsDragging] = useState(false);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        if (!isLoading) setIsDragging(true);
    };

    const handleDragLeave = () => setIsDragging(false);

    const validateAndAddFiles = (newFiles: File[]) => {
        const validFiles = newFiles.filter((file) => file.type.startsWith("image/"));
        if (validFiles.length !== newFiles.length) {
            toast.error("Solo se permiten archivos de imagen.");
        }

        if (files.length + validFiles.length > 8) {
            toast.error("Máximo 8 imágenes permitidas.");
            return;
        }

        setFiles((prev) => [...prev, ...validFiles]);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (isLoading) return;

        const droppedFiles = Array.from(e.dataTransfer.files);
        validateAndAddFiles(droppedFiles);
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const selectedFiles = Array.from(e.target.files);
            validateAndAddFiles(selectedFiles);
        }
    };

    const removeFile = (index: number) => {
        setFiles((prev) => prev.filter((_, i) => i !== index));
    };

    return (
        <div className="w-full max-w-2xl mx-auto space-y-6">
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={clsx(
                    "relative border-2 border-dashed rounded-xl p-8 transition-all duration-300 text-center cursor-pointer",
                    isDragging ? "border-zinc-500 bg-zinc-100/50 scale-[1.01]" : "border-zinc-200 hover:border-zinc-300 bg-white",
                    isLoading && "opacity-50 cursor-not-allowed pointer-events-none"
                )}
            >
                <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleFileSelect}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
                    disabled={isLoading}
                />
                <div className="flex flex-col items-center gap-4">
                    <div className="p-4 rounded-full bg-zinc-50">
                        <Upload className="w-6 h-6 text-zinc-400" />
                    </div>
                    <div className="space-y-1">
                        <p className="font-medium text-zinc-900">Arrastra tus fotos aquí</p>
                        <p className="text-sm text-zinc-500">o haz clic para seleccionar (Máx. 8)</p>
                    </div>
                </div>
            </div>

            <AnimatePresence>
                {files.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="grid grid-cols-4 sm:grid-cols-6 gap-4"
                    >
                        {files.map((file, index) => (
                            <motion.div
                                key={`${file.name}-${index}`}
                                initial={{ scale: 0.8, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                exit={{ scale: 0.8, opacity: 0 }}
                                className="relative aspect-square group rounded-lg overflow-hidden border border-zinc-200 bg-zinc-50"
                            >
                                <img
                                    src={URL.createObjectURL(file)}
                                    alt="Preview"
                                    className="w-full h-full object-cover"
                                />
                                {!isLoading && (
                                    <button
                                        onClick={() => removeFile(index)}
                                        className="absolute top-1 right-1 p-1 rounded-full bg-black/50 text-white opacity-0 group-hover:opacity-100 transition-opacity hover:bg-black/70"
                                    >
                                        <X className="w-3 h-3" />
                                    </button>
                                )}
                            </motion.div>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>

            {files.length > 0 && (
                <motion.button
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    onClick={() => onStart(files)}
                    disabled={isLoading}
                    className="w-full py-3 rounded-lg bg-zinc-900 text-white font-medium hover:bg-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    {isLoading ? "Enviando..." : "Generar Panel"}
                </motion.button>
            )}
        </div>
    );
}
