import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

/**
 * Cloud configuration for Cloudflare R2
 * Free tier: 10GB storage, 1M requests/month
 */
export const R2_CONFIG = {
    endpoint: import.meta.env.VITE_R2_ENDPOINT || '',
    publicUrl: import.meta.env.VITE_R2_PUBLIC_URL || '',
    bucket: import.meta.env.VITE_R2_BUCKET || 'angels-ai-results',
    freeLimit: 10 * 1024 * 1024 * 1024  // 10GB
};

/**
 * API configuration for fallback (Flash mode)
 */
export const API_CONFIG = {
    openai: {
        endpoint: 'https://api.openai.com/v1/chat/completions',
        model: 'gpt-3.5-turbo',
        costPer1kTokens: 0.0015  // $0.0015 per 1K tokens
    },
    anthropic: {
        endpoint: 'https://api.anthropic.com/v1/messages',
        model: 'claude-3-haiku-20240307',
        costPer1kTokens: 0.00025  // $0.00025 per 1K tokens (cheaper)
    }
};

/**
 * Storage limits per mode
 */
export const STORAGE_LIMITS = {
    core: {
        local: Infinity,  // No cloud storage
        cloud: 0
    },
    hybrid: {
        local: 100 * 1024 * 1024,  // 100MB local cache
        cloud: 10 * 1024 * 1024 * 1024  // 10GB R2 free tier
    },
    flash: {
        local: 50 * 1024 * 1024,  // 50MB local cache
        cloud: 10 * 1024 * 1024 * 1024  // 10GB R2 free tier
    }
};
