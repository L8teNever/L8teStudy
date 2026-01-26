/**
 * Google Drive OAuth Integration
 * Simplified: Shows ALL files from the authenticated Google Drive account
 * Added: RAM Caching for faster navigation
 */

class DriveManager {
    constructor() {
        this.authenticated = false;
        this.files = [];
        this.nextPageToken = null;
        this.currentParentId = 'root';
        this.history = []; // For breadcrumbs

        // RAM Cache
        this.cache = new Map();
        this.cacheDuration = 1000 * 60 * 60 * 24; // 24 hours cache

        this.init();
    }

    async init() {
        await this.checkAuthStatus();
    }

    async checkAuthStatus() {
        try {
            const response = await fetch('/api/drive/auth/status');
            const data = await response.json();
            this.authenticated = data.authenticated;
            this.authMethod = data.method; // 'oauth' or 'service_account'
            return this.authenticated;
        } catch (error) {
            console.error('Failed to check auth status:', error);
            return false;
        }
    }

    async startOAuth() {
        try {
            const response = await fetch('/api/drive/auth/start');
            const data = await response.json();

            if (data.authorization_url) {
                // Open OAuth in popup
                const width = 600;
                const height = 700;
                const left = (screen.width - width) / 2;
                const top = (screen.height - height) / 2;

                const popup = window.open(
                    data.authorization_url,
                    'Google Drive OAuth',
                    `width=${width},height=${height},left=${left},top=${top}`
                );

                // Listen for OAuth completion
                const checkPopup = setInterval(() => {
                    if (popup.closed) {
                        clearInterval(checkPopup);
                        this.checkAuthStatus().then(() => {
                            if (this.authenticated) {
                                showNotification('Google Drive erfolgreich verbunden!', 'success');
                                this.clearCache(); // Clear cache after new auth
                            }
                        });
                    }
                }, 500);
            }
        } catch (error) {
            console.error('OAuth start failed:', error);
            showNotification('OAuth-Fehler', 'error');
        }
    }

    async revokeAuth() {
        if (!confirm('Möchten Sie die Google Drive Verbindung wirklich trennen?')) {
            return;
        }

        try {
            const response = await fetch('/api/drive/auth/revoke', {
                method: 'POST'
            });

            if (response.ok) {
                this.authenticated = false;
                this.files = [];
                this.clearCache();
                showNotification('Google Drive Verbindung getrennt', 'success');
            }
        } catch (error) {
            console.error('Revoke failed:', error);
            showNotification('Fehler beim Trennen', 'error');
        }
    }

    clearCache() {
        this.cache.clear();
    }

    async loadFiles(parentId = 'root', pageToken = null) {
        // Check cache first (only for first page of a folder)
        if (!pageToken) {
            const cached = this.cache.get(parentId);
            if (cached && (Date.now() - cached.timestamp < this.cacheDuration)) {
                console.log('Loading from RAM cache:', parentId);
                this.currentParentId = parentId;
                this.files = cached.data.files;
                this.nextPageToken = cached.data.nextPageToken;
                return {
                    files: this.files,
                    nextPageToken: this.nextPageToken,
                    parentId: parentId,
                    cached: true
                };
            }
        }

        try {
            this.currentParentId = parentId;
            let url = `/api/drive/files?parent_id=${parentId}`;
            if (pageToken) {
                url += `&pageToken=${pageToken}`;
            }

            const response = await fetch(url);
            const data = await response.json();

            if (data.success) {
                if (pageToken) {
                    this.files = this.files.concat(data.files);
                } else {
                    this.files = data.files;
                    // Save to cache
                    this.cache.set(parentId, {
                        timestamp: Date.now(),
                        data: {
                            files: data.files,
                            nextPageToken: data.nextPageToken
                        }
                    });
                }
                this.nextPageToken = data.nextPageToken;
                return {
                    files: this.files,
                    nextPageToken: this.nextPageToken,
                    parentId: parentId
                };
            }
            return { files: [], nextPageToken: null };
        } catch (error) {
            console.error('Failed to load files:', error);
            return { files: [], nextPageToken: null };
        }
    }

    async loadMoreFiles() {
        if (!this.nextPageToken) {
            return null;
        }
        return await this.loadFiles(this.currentParentId, this.nextPageToken);
    }

    async searchFiles(query) {
        // Search is usually too dynamic for simple caching, 
        // but we could cache the exact query if needed.
        const cacheKey = `search_${query}`;
        const cached = this.cache.get(cacheKey);
        if (cached && (Date.now() - cached.timestamp < this.cacheDuration)) {
            return cached.data;
        }

        try {
            const response = await fetch(`/api/drive/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.success) {
                this.cache.set(cacheKey, {
                    timestamp: Date.now(),
                    data: data.files
                });
                return data.files;
            }
            return [];
        } catch (error) {
            console.error('Search failed:', error);
            return [];
        }
    }

    getFileIcon(mimeType) {
        const iconMap = {
            'application/pdf': '📄',
            'application/vnd.google-apps.document': '📝',
            'application/vnd.google-apps.spreadsheet': '📊',
            'application/vnd.google-apps.presentation': '📽️',
            'application/vnd.google-apps.folder': '📁',
            'image/': '🖼️',
            'video/': '🎥',
            'audio/': '🎵'
        };

        for (const [key, icon] of Object.entries(iconMap)) {
            if (mimeType.startsWith(key)) {
                return icon;
            }
        }
        return '📎';
    }

    formatFileSize(bytes) {
        if (!bytes) return '-';
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }

    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('de-DE', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Global instance
let driveManager = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    driveManager = new DriveManager();

    // Check for OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('drive_auth') === 'success') {
        showNotification('Google Drive erfolgreich verbunden!', 'success');
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    } else if (urlParams.get('drive_auth') === 'error') {
        showNotification('Google Drive Verbindung fehlgeschlagen', 'error');
        window.history.replaceState({}, document.title, window.location.pathname);
    }
});
