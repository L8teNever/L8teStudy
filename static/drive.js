// ============================================
// DRIVE MANAGER - L8teStudy
// ============================================
// Handles Google Drive OAuth integration on the frontend

class DriveManager {
    constructor() {
        this.authenticated = false;
        this.authMethod = 'oauth'; // Default
        this.currentFolderId = null;
        this.currentPageToken = null;
        this.history = [];
    }

    async checkAuthStatus() {
        try {
            const response = await fetch('/api/drive/auth/status');
            const data = await response.json();
            this.authenticated = data.authenticated || false;
            this.authMethod = data.method || 'oauth';
            return this.authenticated;
        } catch (error) {
            console.error('Error checking auth status:', error);
            this.authenticated = false;
            return false;
        }
    }

    async startOAuth() {
        try {
            const response = await fetch('/api/drive/auth/start');
            const data = await response.json();

            if (data.auth_url) {
                // Open OAuth popup
                const width = 600;
                const height = 700;
                const left = (screen.width / 2) - (width / 2);
                const top = (screen.height / 2) - (height / 2);

                const popup = window.open(
                    data.auth_url,
                    'Google Drive OAuth',
                    `width=${width},height=${height},left=${left},top=${top}`
                );

                // Poll for popup close
                const pollTimer = setInterval(() => {
                    if (popup.closed) {
                        clearInterval(pollTimer);
                        this.checkAuthStatus().then(authenticated => {
                            if (authenticated) {
                                if (typeof showToast === 'function') {
                                    showToast('✅ Google Drive verbunden!', 'success');
                                }
                                // Reload current view if it's drive-related
                                if (typeof currentView !== 'undefined' && (currentView === 'drive' || currentView === 'sub_drive_auth')) {
                                    if (currentView === 'drive') renderDrive();
                                    else if (currentView === 'sub_drive_auth') renderDriveAuthSettings();
                                }
                            }
                        });
                    }
                }, 500);
            }
        } catch (error) {
            console.error('Error starting auth:', error);
            if (typeof showToast === 'function') {
                showToast('Fehler beim Verbinden mit Google Drive', 'error');
            }
        }
    }

    async revokeAuth() {
        try {
            const response = await fetch('/api/drive/auth/revoke', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.success) {
                this.authenticated = false;
                if (typeof showToast === 'function') {
                    showToast('Google Drive Verbindung getrennt', 'success');
                }
                return true;
            }
            return false;
        } catch (error) {
            console.error('Error revoking auth:', error);
            return false;
        }
    }

    async loadFiles(parentId = 'root', pageToken = null) {
        try {
            let url = `/api/drive/browse?parent_id=${parentId}`;
            if (pageToken) {
                url += `&page_token=${pageToken}`;
            }

            const response = await fetch(url);
            const data = await response.json();

            this.currentPageToken = data.nextPageToken || null;
            this.currentFolderId = parentId;

            return {
                files: data.items || [],
                nextPageToken: data.nextPageToken || null
            };
        } catch (error) {
            console.error('Error loading files:', error);
            return { files: [], nextPageToken: null };
        }
    }

    async loadMoreFiles() {
        if (!this.currentPageToken) return { files: [], nextPageToken: null };
        return this.loadFiles(this.currentFolderId, this.currentPageToken);
    }

    async searchFiles(query) {
        try {
            const response = await fetch(`/api/drive/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            this.currentPageToken = null; // No pagination in search results currently
            return data.files || [];
        } catch (error) {
            console.error('Error searching files:', error);
            return [];
        }
    }

    async getLinkedFolders() {
        try {
            const response = await fetch('/api/drive/folders');
            const data = await response.json();

            // Transform folder data to look like file items
            const folders = data.folders || [];
            return folders.map(folder => ({
                id: folder.folder_id,
                name: folder.name,
                mimeType: 'application/vnd.google-apps.folder',
                webViewLink: `https://drive.google.com/drive/folders/${folder.folder_id}`,
                isLinked: true,
                subject: folder.subject_name,
                fileCount: folder.file_count
            }));
        } catch (error) {
            console.error('Error loading linked folders:', error);
            return [];
        }
    }

    async getFileMetadata(fileId) {
        try {
            const response = await fetch(`/api/drive/file/${fileId}`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error getting file metadata:', error);
            return null;
        }
    }

    getFileIcon(mimeType) {
        if (!mimeType) return 'file';
        if (mimeType.includes('folder')) return 'folder';
        if (mimeType.includes('pdf')) return 'file-text';
        if (mimeType.includes('image')) return 'image';
        if (mimeType.includes('video')) return 'video';
        if (mimeType.includes('audio')) return 'music';
        if (mimeType.includes('word') || mimeType.includes('document')) return 'file-text';
        if (mimeType.includes('spreadsheet') || mimeType.includes('excel')) return 'file-spreadsheet';
        if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) return 'monitor';
        return 'file';
    }

    formatDate(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
    }

    formatFileSize(bytes) {
        if (!bytes) return '';
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) return '0 B';
        const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
        return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
    }
}

// Create global instance
window.driveManager = new DriveManager();

console.log('Drive Manager initialized');
