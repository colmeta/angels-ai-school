/**
 * Audio Utilities
 * ===============
 * Helpers for processing audio for Edge AI (Whisper).
 */

/**
 * Converts a MediaRecorder blob to a Float32Array of 16kHz PCM audio.
 */
export async function blobToFloat32Array(blob: Blob): Promise<Float32Array> {
    const arrayBuffer = await blob.arrayBuffer();
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });

    try {
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
        const float32Data = audioBuffer.getChannelData(0); // Get first channel
        return float32Data;
    } finally {
        await audioContext.close();
    }
}
