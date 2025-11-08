/**
 * Voice Input Component
 * Press & hold to record voice commands
 */
import { useState } from 'react';
import { useVoiceCommands } from '@/hooks/useVoiceCommands';

interface VoiceInputProps {
  schoolId: string;
  onResult?: (result: any) => void;
  onError?: (error: string) => void;
  disabled?: boolean;
}

export function VoiceInput({ schoolId, onResult, onError, disabled }: VoiceInputProps) {
  const [feedback, setFeedback] = useState<string>('');
  const [feedbackType, setFeedbackType] = useState<'success' | 'error' | 'info'>('info');

  const {
    isSupported,
    isListening,
    isProcessing,
    transcript,
    startListening,
    stopListening,
  } = useVoiceCommands({
    schoolId,
    onResult: (result) => {
      if (result.success) {
        setFeedback(`✅ ${result.command || 'Command executed successfully'}`);
        setFeedbackType('success');
      } else {
        setFeedback(`❌ ${result.error || 'Command failed'}`);
        setFeedbackType('error');
      }
      onResult?.(result);

      // Clear feedback after 5 seconds
      setTimeout(() => setFeedback(''), 5000);
    },
    onError: (error) => {
      setFeedback(`❌ ${error}`);
      setFeedbackType('error');
      onError?.(error);
      setTimeout(() => setFeedback(''), 5000);
    },
  });

  if (!isSupported) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
        <p className="font-medium">⚠️ Voice commands not supported</p>
        <p className="mt-1">Your browser doesn't support voice recognition. Please use Chrome, Safari, or Edge.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Voice Button */}
      <div className="flex items-center justify-center">
        <button
          type="button"
          onMouseDown={startListening}
          onMouseUp={stopListening}
          onTouchStart={startListening}
          onTouchEnd={stopListening}
          disabled={disabled || isProcessing}
          className={`
            relative w-20 h-20 rounded-full flex items-center justify-center
            transition-all duration-200 shadow-lg
            ${isListening 
              ? 'bg-red-500 scale-110 animate-pulse' 
              : 'bg-blue-500 hover:bg-blue-600 active:scale-95'
            }
            ${disabled || isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          `}
        >
          {isProcessing ? (
            <svg className="w-8 h-8 text-white animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          ) : (
            <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
            </svg>
          )}
        </button>
      </div>

      {/* Instructions */}
      <div className="text-center">
        <p className="text-sm font-medium text-gray-700">
          {isListening ? (
            <span className="text-red-600">🎤 Listening... Release to send</span>
          ) : isProcessing ? (
            <span className="text-blue-600">⏳ Processing command...</span>
          ) : (
            <span className="text-gray-600">Press & hold to speak</span>
          )}
        </p>
      </div>

      {/* Live Transcript */}
      {transcript && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 min-h-[60px]">
          <p className="text-sm text-gray-600 mb-1">You said:</p>
          <p className="text-base font-medium text-gray-900">{transcript}</p>
        </div>
      )}

      {/* Feedback */}
      {feedback && (
        <div
          className={`
            border rounded-lg p-3
            ${feedbackType === 'success' ? 'bg-green-50 border-green-200 text-green-800' : ''}
            ${feedbackType === 'error' ? 'bg-red-50 border-red-200 text-red-800' : ''}
            ${feedbackType === 'info' ? 'bg-blue-50 border-blue-200 text-blue-800' : ''}
          `}
        >
          <p className="text-sm font-medium">{feedback}</p>
        </div>
      )}

      {/* Example Commands */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <p className="text-sm font-medium text-blue-900 mb-2">📝 Example Commands:</p>
        <ul className="text-xs text-blue-800 space-y-1">
          <li>• "Mark John as present"</li>
          <li>• "Mark all Class 5A as present"</li>
          <li>• "Record 85 marks for Mary in Math"</li>
          <li>• "Send message to all parents: School closes early"</li>
        </ul>
      </div>
    </div>
  );
}
