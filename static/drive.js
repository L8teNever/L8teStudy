// ============================================
// DRIVE MANAGER - L8teStudy
// ============================================
// Handles Google Drive OAuth integration on the frontend

class DriveManager {
    constructor() {
        this.authenticated = false;
        this.currentFolderId = null;
        this.currentPageToken = null;
        this.history = [];
    }

    async checkAuthStatus() {
        try {
            const response = await fetch('/api/drive/auth/status');
            const data = await response.json();
            this.authenticated = data.authenticated || false;
            return this.authenticated;
        } catch (error) {
            console.error('Error checking auth status:', error);
            this.authenticated = false;
            return false;
        }
    }

    async startAuth() {
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
                                if (typeof currentView !== 'undefined' && currentView.includes('drive')) {
                                    if (typeof renderDrive === 'function') {
                                        renderDrive();
                                    }
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

            return {
                files: data.items || [],
                nextPageToken: data.nextPageToken || null
            };
        } catch (error) {
            console.error('Error loading files:', error);
            return { files: [], nextPageToken: null };
        }
    }

    async searchFiles(query) {
        try {
            const response = await fetch(`/api/drive/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
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
}

// Create global instance
const driveManager = new DriveManager();

console.log('Drive Manager initialized');
