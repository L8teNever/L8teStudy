/**
 * Google Drive OAuth Integration
 * Handles Drive authentication, folder selection, and file display
 */

class DriveManager {
    constructor() {
        this.authenticated = false;
        this.selectedFolders = [];
        this.files = [];
        this.init();
    }

    async init() {
        await this.checkAuthStatus();
        if (this.authenticated) {
            await this.loadSelectedFolders();
        }
    }

    async checkAuthStatus() {
        try {
            const response = await fetch('/api/drive/auth/status');
            const data = await response.json();
            this.authenticated = data.authenticated;
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
                                this.loadSelectedFolders();
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
                this.selectedFolders = [];
                this.files = [];
                showNotification('Google Drive Verbindung getrennt', 'success');
            }
        } catch (error) {
            console.error('Revoke failed:', error);
            showNotification('Fehler beim Trennen', 'error');
        }
    }

    async browseFolders(parentId = 'root') {
        try {
            const response = await fetch(`/api/drive/browse?parent_id=${parentId}`);
            const data = await response.json();

            if (data.success) {
                return data.folders;
            }
            return [];
        } catch (error) {
            console.error('Browse failed:', error);
            return [];
        }
    }

    async loadSelectedFolders() {
        try {
            const response = await fetch('/api/drive/folders');
            this.selectedFolders = await response.json();
            return this.selectedFolders;
        } catch (error) {
            console.error('Failed to load folders:', error);
            return [];
        }
    }

    async addFolder(driveFolderId, folderName, subjectId = null, includeSubfolders = true) {
        try {
            const response = await fetch('/api/drive/folders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    drive_folder_id: driveFolderId,
                    folder_name: folderName,
                    subject_id: subjectId,
                    include_subfolders: includeSubfolders
                })
            });

            const data = await response.json();

            if (data.success) {
                await this.loadSelectedFolders();
                showNotification('Ordner hinzugefügt', 'success');
                return true;
            } else {
                showNotification(data.message || 'Fehler beim Hinzufügen', 'error');
                return false;
            }
        } catch (error) {
            console.error('Add folder failed:', error);
            showNotification('Fehler beim Hinzufügen', 'error');
            return false;
        }
    }

    async removeFolder(folderId) {
        if (!confirm('Ordner wirklich entfernen?')) {
            return;
        }

        try {
            const response = await fetch(`/api/drive/folders/${folderId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                await this.loadSelectedFolders();
                showNotification('Ordner entfernt', 'success');
            }
        } catch (error) {
            console.error('Remove folder failed:', error);
            showNotification('Fehler beim Entfernen', 'error');
        }
    }

    async updateFolder(folderId, updates) {
        try {
            const response = await fetch(`/api/drive/folders/${folderId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates)
            });

            if (response.ok) {
                await this.loadSelectedFolders();
                showNotification('Ordner aktualisiert', 'success');
            }
        } catch (error) {
            console.error('Update folder failed:', error);
            showNotification('Fehler beim Aktualisieren', 'error');
        }
    }

    async loadFiles() {
        try {
            const response = await fetch('/api/drive/files');
            const data = await response.json();

            if (data.success) {
                this.files = data.files;
                return this.files;
            }
            return [];
        } catch (error) {
            console.error('Failed to load files:', error);
            return [];
        }
    }

    async searchFiles(query) {
        try {
            const response = await fetch(`/api/drive/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.success) {
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
