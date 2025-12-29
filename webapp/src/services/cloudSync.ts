/**
 * Cloud Sync Service (Cloudflare R2 Free Tier)
 * Syncs AI results to cloud storage for cross-device access
 */

export interface AIResult {
    id: string;
    schoolId: string;
    userId: string;
    intent: any;
    metadata: {
        mode: 'core' | 'hybrid' | 'flash';
        timestamp: number;
        processingTime: number;
        source: 'local' | 'cloud';
    };
}

export class CloudSyncService {
    private schoolId: string;
    private userId: string;
    private syncEnabled: boolean;
    private pendingSync: AIResult[] = [];
    private r2Endpoint: string;

    constructor(schoolId: string, userId: string) {
        this.schoolId = schoolId;
        this.userId = userId;
        this.syncEnabled = this.checkSyncEnabled();
        // Cloudflare R2 endpoint (will be configured in env)
        this.r2Endpoint = import.meta.env.VITE_R2_ENDPOINT || '';

        // Start sync worker
        if (this.syncEnabled && navigator.onLine) {
            this.startBackgroundSync();
        }

        // Listen for online/offline events
        window.addEventListener('online', () => this.onOnline());
        window.addEventListener('offline', () => this.onOffline());
    }

    private checkSyncEnabled(): boolean {
        const aiMode = localStorage.getItem('ai_mode');
        return aiMode === 'hybrid' || aiMode === 'flash';
    }

    /**
     * Store result locally first (offline-first)
     */
    async storeLocal(result: AIResult): Promise<void> {
        try {
            const db = await this.openDB();
            const tx = db.transaction('ai_results', 'readwrite');
            const store = tx.objectStore('ai_results');
            await store.put(result);

            // Queue for sync if online
            if (this.syncEnabled && navigator.onLine) {
                this.pendingSync.push(result);
            }
        } catch (error) {
            console.error('[CloudSync] Failed to store locally:', error);
        }
    }

    /**
     * Upload to Cloudflare R2
     */
    async uploadToCloud(result: AIResult): Promise<void> {
        if (!this.syncEnabled || !this.r2Endpoint) {
            return;
        }

        try {
            const key = `schools/${this.schoolId}/users/${this.userId}/results/${result.id}.json`;

            const response = await fetch(`${this.r2Endpoint}/upload`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${await this.getAuthToken()}`
                },
                body: JSON.stringify({
                    key,
                    data: result
                })
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            console.log('[CloudSync] Uploaded:', result.id);
        } catch (error) {
            console.error('[CloudSync] Upload failed:', error);
            // Keep in pending queue for retry
            this.pendingSync.push(result);
        }
    }

    /**
     * Sync result (store local, then cloud)
     */
    async syncResult(result: AIResult): Promise<void> {
        await this.storeLocal(result);

        if (this.syncEnabled && navigator.onLine) {
            await this.uploadToCloud(result);
        }
    }

    /**
     * Background sync worker
     */
    private async startBackgroundSync(): Promise<void> {
        setInterval(async () => {
            if (this.pendingSync.length > 0 && navigator.onLine) {
                const batch = this.pendingSync.splice(0, 10);  // Sync 10 at a time

                for (const result of batch) {
                    await this.uploadToCloud(result);
                }
            }
        }, 30000);  // Every 30 seconds
    }

    /**
     * Get storage quota status
     */
    async getQuotaStatus(): Promise<{ used: number; limit: number; percentage: number }> {
        try {
            const response = await fetch(`${this.r2Endpoint}/quota`, {
                headers: {
                    'Authorization': `Bearer ${await this.getAuthToken()}`
                }
            });

            const data = await response.json();
            return {
                used: data.used_bytes,
                limit: 10 * 1024 * 1024 * 1024,  // 10GB R2 free tier
                percentage: (data.used_bytes / (10 * 1024 * 1024 * 1024)) * 100
            };
        } catch (error) {
            console.error('[CloudSync] Failed to get quota:', error);
            return { used: 0, limit: 10737418240, percentage: 0 };
        }
    }

    /**
     * Fetch results from cloud
     */
    async fetchFromCloud(limit: number = 100): Promise<AIResult[]> {
        if (!this.syncEnabled || !this.r2Endpoint) {
            return [];
        }

        try {
            const response = await fetch(
                `${this.r2Endpoint}/list?prefix=schools/${this.schoolId}/users/${this.userId}/results/&limit=${limit}`,
                {
                    headers: {
                        'Authorization': `Bearer ${await this.getAuthToken()}`
                    }
                }
            );

            const data = await response.json();
            return data.results || [];
        } catch (error) {
            console.error('[CloudSync] Failed to fetch from cloud:', error);
            return [];
        }
    }

    /**
     * Handle online event
     */
    private onOnline(): void {
        console.log('[CloudSync] Device online, starting sync');
        this.startBackgroundSync();
    }

    /**
     * Handle offline event
     */
    private onOffline(): void {
        console.log('[CloudSync] Device offline, sync paused');
    }

    /**
     * Open IndexedDB for local storage
     */
    private async openDB(): Promise<IDBDatabase> {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('angels_ai_db', 1);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result);

            request.onupgradeneeded = (event) => {
                const db = (event.target as IDBOpenDBRequest).result;
                if (!db.objectStoreNames.contains('ai_results')) {
                    db.createObjectStore('ai_results', { keyPath: 'id' });
                }
            };
        });
    }

    /**
     * Get auth token for R2 requests
     */
    private async getAuthToken(): Promise<string> {
        // Get from localStorage or session
        return localStorage.getItem('auth_token') || '';
    }
}

/**
 * Singleton instance
 */
let cloudSyncInstance: CloudSyncService | null = null;

export function getCloudSyncService(schoolId?: string, userId?: string): CloudSyncService {
    if (!cloudSyncInstance && schoolId && userId) {
        cloudSyncInstance = new CloudSyncService(schoolId, userId);
    }
    return cloudSyncInstance!;
}
