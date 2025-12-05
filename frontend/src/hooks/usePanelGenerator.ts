"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { toast } from "sonner";
import { JobResponse, JobStatus } from "../types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "";

// Clean WS URL to avoid duplications like /ws/ws/
const getWsUrl = (jobId: string) => {
    let baseUrl = WS_URL;
    if (typeof window !== "undefined" && window.location.protocol === "https:") {
        baseUrl = baseUrl.replace(/^ws:\/\//, "wss://");
    }

    // Remove trailing slashes
    baseUrl = baseUrl.replace(/\/+$/, "");

    // Check if baseUrl already ends with /ws to avoid duplication
    if (baseUrl.endsWith("/ws")) {
        return `${baseUrl}/${jobId}`;
    }

    return `${baseUrl}/ws/${jobId}`;
};

export function usePanelGenerator() {
    const [status, setStatus] = useState<JobStatus | null>(null);
    const [jobId, setJobId] = useState<string | null>(null);
    const [resultUrl, setResultUrl] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

    // Restore session
    useEffect(() => {
        const savedJobId = localStorage.getItem("panel_one_job_id");
        if (savedJobId) {
            setJobId(savedJobId);
            // Immediately fetch status to restore UI state
            fetchJobStatus(savedJobId);
        }
    }, []);

    const clearSession = useCallback(() => {
        localStorage.removeItem("panel_one_job_id");
        setJobId(null);
        setStatus(null);
        setResultUrl(null);
        setError(null);
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
        }
    }, []);

    const fetchJobStatus = async (id: string) => {
        try {
            const res = await fetch(`${API_URL}/job/${id}`);
            if (res.status === 503) {
                throw new Error("Service Unavailable");
            }
            if (!res.ok) {
                throw new Error(`Error ${res.status}`);
            }
            const data: JobResponse = await res.json();
            handleStateUpdate(data);
        } catch (err) {
            console.error("Watchdog error:", err);
            // Critical error handling
            if (err instanceof Error && (err.message.includes("503") || err.message.includes("Service Unavailable"))) {
                toast.error("Servicio no disponible. Intentando limpiar sesión.");
                clearSession();
            }
        }
    };

    const handleStateUpdate = (data: JobResponse) => {
        setStatus(data.status);
        if (data.result_url) setResultUrl(data.result_url);
        if (data.error_message) setError(data.error_message);

        if (data.status === "COMPLETED" || data.status === "FAILED") {
            // Stop polling and WS ?? Or keep them open?
            // Usually stop for completed/failed.
            if (pollIntervalRef.current) {
                clearInterval(pollIntervalRef.current);
                pollIntervalRef.current = null;
            }
            if (wsRef.current) {
                wsRef.current.close();
                wsRef.current = null;
            }
            // If completed, keep session? No, maybe keep it to show result until reset.
            // If Failed, allow reset.

            // But we should NOT clear localStorage automatically on Completed, 
            // because if user reloads they want to see the image.
            // User must click "Restart" to clear.
        }
    };

    // WebSocket Connection
    useEffect(() => {
        if (!jobId || status === "COMPLETED" || status === "FAILED") return;

        const url = getWsUrl(jobId);
        console.log("Connecting WS:", url);
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onmessage = (event) => {
            try {
                const data: JobResponse = JSON.parse(event.data);
                handleStateUpdate(data);
            } catch (e) {
                console.error("WS Parse error", e);
            }
        };

        ws.onerror = (e) => {
            console.error("WS Error", e);
        };

        return () => {
            ws.close();
        };
    }, [jobId]);

    // Watchdog Polling
    useEffect(() => {
        if (!jobId || status === "COMPLETED" || status === "FAILED") {
            if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
            return;
        }

        // Initial fetch
        fetchJobStatus(jobId);

        pollIntervalRef.current = setInterval(() => {
            fetchJobStatus(jobId);
        }, 5000);

        return () => {
            if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
        };
    }, [jobId]);


    const startJob = async (files: File[]) => {
        try {
            setStatus("QUEUED"); // Optimistic update
            const formData = new FormData();
            files.forEach((file) => formData.append("images", file));

            const res = await fetch(`${API_URL}/generate`, {
                method: "POST",
                body: formData,
            });

            if (!res.ok) throw new Error("Failed to start generation");

            const data: JobResponse = await res.json();
            setJobId(data.job_id);
            localStorage.setItem("panel_one_job_id", data.job_id);
            handleStateUpdate(data);
        } catch (err) {
            console.error(err);
            toast.error("Error al iniciar la generación.");
            setStatus("FAILED");
            setError(err instanceof Error ? err.message : "Error desconocido");
        }
    };

    return {
        status,
        resultUrl,
        error,
        startJob,
        reset: clearSession,
    };
}
