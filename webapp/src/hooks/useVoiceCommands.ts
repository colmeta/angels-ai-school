/**
 * Voice Commands Hook
 * Speech-to-text → Command execution
 * 
 * Examples:
 * - "Mark John as present"
 * - "Record 85 marks for Mary in Math"
 * - "Mark all Class 5A as present"
 */
import { useState, useCallback, useEffect } from 'react';
import { apiClient } from '@/lib/apiClient';

interface VoiceCommandResult {
  success: boolean;
  transcript: string;
  command?: string;
  result?: any;
  error?: string;
}

interface UseVoiceCommandsOptions {
  schoolId: string;
  onResult?: (result: VoiceCommandResult) => void;
  onError?: (error: string) => void;
  language?: string;
}

export function useVoiceCommands(options: UseVoiceCommandsOptions) {
  const { schoolId, onResult, onError, language = 'en-US' } = options;
  
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);
  const [isSupported, setIsSupported] = useState(false);

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Check browser support
    const SpeechRecognition = 
      (window as any).SpeechRecognition || 
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setIsSupported(false);
      return;
    }

    setIsSupported(true);

    const recognitionInstance = new SpeechRecognition();
    recognitionInstance.continuous = false;
    recognitionInstance.interimResults = true;
    recognitionInstance.lang = language;

    recognitionInstance.onresult = (event: any) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
        } else {
          interimTranscript += transcript;
        }
      }

      // Update transcript in real-time
      setTranscript(interimTranscript || finalTranscript);

      // If final result, process command
      if (finalTranscript) {
        processCommand(finalTranscript.trim());
      }
    };

    recognitionInstance.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      
      let errorMessage = 'Voice recognition error';
      if (event.error === 'no-speech') {
        errorMessage = 'No speech detected. Please try again.';
      } else if (event.error === 'network') {
        errorMessage = 'Network error. Check your internet connection.';
      } else if (event.error === 'not-allowed') {
        errorMessage = 'Microphone access denied. Please allow microphone access.';
      }
      
      onError?.(errorMessage);
    };

    recognitionInstance.onend = () => {
      setIsListening(false);
    };

    setRecognition(recognitionInstance);

    return () => {
      if (recognitionInstance) {
        recognitionInstance.abort();
      }
    };
  }, [language, onError]);

  // Start listening
  const startListening = useCallback(() => {
    if (!recognition || isListening) return;

    try {
      setTranscript('');
      setIsListening(true);
      recognition.start();
    } catch (error) {
      console.error('Error starting recognition:', error);
      setIsListening(false);
      onError?.('Could not start voice recognition');
    }
  }, [recognition, isListening, onError]);

  // Stop listening
  const stopListening = useCallback(() => {
    if (!recognition || !isListening) return;

    try {
      recognition.stop();
      setIsListening(false);
    } catch (error) {
      console.error('Error stopping recognition:', error);
    }
  }, [recognition, isListening]);

  // Process command via API
  const processCommand = useCallback(async (command: string) => {
    if (!command || isProcessing) return;

    setIsProcessing(true);

    try {
      const response = await apiClient.post('/command/execute', {
        command,
        school_id: schoolId,
      });

      const result: VoiceCommandResult = {
        success: response.data.success,
        transcript: command,
        command: response.data.intent || command,
        result: response.data.result,
      };

      onResult?.(result);
    } catch (error: any) {
      const errorResult: VoiceCommandResult = {
        success: false,
        transcript: command,
        error: error.response?.data?.detail || error.message || 'Command execution failed',
      };

      onResult?.(errorResult);
      onError?.(errorResult.error!);
    } finally {
      setIsProcessing(false);
    }
  }, [schoolId, isProcessing, onResult, onError]);

  // Manual command execution (for testing or typing)
  const executeCommand = useCallback(async (command: string) => {
    await processCommand(command);
  }, [processCommand]);

  return {
    isSupported,
    isListening,
    isProcessing,
    transcript,
    startListening,
    stopListening,
    executeCommand,
  };
}
