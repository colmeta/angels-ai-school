import { useState, useCallback, useEffect, useRef } from 'react';
import { localAgent } from '../services/LocalAgentService';
import { blobToFloat32Array } from '../utils/audioUtils';
export function useVoiceCommands(options) {
    const { schoolId, onResult, onError } = options;
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [isSupported, setIsSupported] = useState(true);
    const mediaRecorder = useRef(null);
    const audioChunks = useRef([]);
    // Subscribe to local transcripts from the AI Worker
    useEffect(() => {
        const unsubscribeTranscript = localAgent.subscribeTranscript((text) => {
            setTranscript(text);
        });
        const unsubscribeResult = localAgent.subscribe((status) => {
            // Handle result via general subscription if needed, 
            // but LocalAgentService 'parse' result is promise-based.
            // However, the worker sends 'RESULT' after 'TRANSCRIPT'.
        });
        // Handle generic results from worker
        const workerListener = (event) => {
            const { type, data } = event.data;
            if (type === 'RESULT') {
                onResult?.({
                    success: true,
                    transcript: transcript,
                    command: data.action,
                    result: data
                });
                setIsProcessing(false);
            }
            if (type === 'ERROR') {
                onError?.(data);
                setIsProcessing(false);
            }
        };
        // Need access to the raw worker for this specific event flow
        // or we could add a `subscribeResult` to LocalAgentService.
        // For now, let's assume LocalAgentService handles it or we use the 'parse' promise.
        return () => {
            unsubscribeTranscript();
            unsubscribeResult();
        };
    }, [onResult, onError, transcript]);
    const startListening = useCallback(async () => {
        if (isListening)
            return;
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder.current = new MediaRecorder(stream);
            audioChunks.current = [];
            mediaRecorder.current.ondataavailable = (event) => {
                audioChunks.current.push(event.data);
            };
            mediaRecorder.current.onstop = async () => {
                const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
                setIsProcessing(true);
                try {
                    const float32Array = await blobToFloat32Array(audioBlob);
                    await localAgent.processVoice(float32Array);
                }
                catch (e) {
                    onError?.(e.message);
                    setIsProcessing(false);
                }
            };
            mediaRecorder.current.start();
            setIsListening(true);
            setTranscript('');
        }
        catch (error) {
            console.error('Error starting recognition:', error);
            setIsListening(false);
            onError?.('Could not access microphone');
        }
    }, [isListening, onError]);
    const stopListening = useCallback(() => {
        if (!mediaRecorder.current || !isListening)
            return;
        mediaRecorder.current.stop();
        setIsListening(false);
        // Stop all tracks to release microphone
        mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
    }, [isListening]);
    return {
        isSupported,
        isListening,
        isProcessing,
        transcript,
        startListening,
        stopListening,
    };
}
