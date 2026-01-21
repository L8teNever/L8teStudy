/**
 * Subject Mapping Manager
 * Manages smart folder name to official subject mappings
 */

class SubjectMappingManager {
    constructor() {
        this.mappings = [];
        this.subjects = [];
        this.init();
    }

    async init() {
        await this.loadSubjects();
        await this.loadMappings();
    }

    async loadSubjects() {
        try {
            const response = await fetch('/api/subjects');
            if (response.ok) {
                this.subjects = await response.json();
            }
        } catch (error) {
            console.error('Error loading subjects:', error);
        }
    }

    async loadMappings() {
        try {
            const response = await fetch('/api/subject-mappings');
            if (response.ok) {
                this.mappings = await response.json();
            }
        } catch (error) {
            console.error('Error loading mappings:', error);
        }
    }

    async createMapping(informalName, subjectId, isGlobal = false) {
        try {
            const response = await fetch('/api/subject-mappings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    informal_name: informalName,
                    subject_id: subjectId,
                    is_global: isGlobal
                })
            });

            if (response.ok) {
                const mapping = await response.json();
                this.mappings.push(mapping);
                return mapping;
            } else {
                const error = await response.json();
                throw new Error(error.message || 'Failed to create mapping');
            }
        } catch (error) {
            console.error('Error creating mapping:', error);
            throw error;
        }
    }

    async updateMapping(id, data) {
        try {
            const response = await fetch(`/api/subject-mappings/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const updated = await response.json();
                const index = this.mappings.findIndex(m => m.id === id);
                if (index !== -1) {
                    this.mappings[index] = updated;
                }
                return updated;
            } else {
                const error = await response.json();
                throw new Error(error.message || 'Failed to update mapping');
            }
        } catch (error) {
            console.error('Error updating mapping:', error);
            throw error;
        }
    }

    async deleteMapping(id) {
        try {
            const response = await fetch(`/api/subject-mappings/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.mappings = this.mappings.filter(m => m.id !== id);
                return true;
            } else {
                const error = await response.json();
                throw new Error(error.message || 'Failed to delete mapping');
            }
        } catch (error) {
            console.error('Error deleting mapping:', error);
            throw error;
        }
    }

    async resolveInformalName(informalName) {
        try {
            const response = await fetch('/api/subject-mappings/resolve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ informal_name: informalName })
            });

            if (response.ok) {
                return await response.json();
            }
            return null;
        } catch (error) {
            console.error('Error resolving informal name:', error);
            return null;
        }
    }

    renderMappingsList(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (this.mappings.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 40px 20px; color: var(--text-sec);">
                    <i data-lucide="folder-search" style="width: 48px; height: 48px; margin-bottom: 16px; opacity: 0.5;"></i>
                    <p style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">Keine Zuordnungen</p>
                    <p style="font-size: 14px;">Erstelle deine erste Fach-Zuordnung</p>
                </div>
            `;
            if (typeof lucide !== 'undefined') lucide.createIcons();
            return;
        }

        const html = this.mappings.map(mapping => `
            <div class="list-item" style="cursor: pointer;" data-mapping-id="${mapping.id}">
                <div class="account-item-icon">
                    <i data-lucide="${mapping.is_global ? 'globe' : 'user'}"></i>
                </div>
                <div class="item-content">
                    <div class="item-title">${this.escapeHtml(mapping.informal_name)}</div>
                    <div class="item-sub">
                        ${this.escapeHtml(mapping.subject_name || 'Unbekanntes Fach')}
                        ${mapping.is_global ? ' • Global' : ' • Persönlich'}
                    </div>
                </div>
                <div style="color: var(--text-sec);">
                    <i data-lucide="chevron-right"></i>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
        if (typeof lucide !== 'undefined') lucide.createIcons();

        // Add click handlers
        container.querySelectorAll('[data-mapping-id]').forEach(item => {
            item.addEventListener('click', () => {
                const id = parseInt(item.dataset.mappingId);
                const mapping = this.mappings.find(m => m.id === id);
                if (mapping) {
                    this.showEditDialog(mapping);
                }
            });
        });
    }

    showEditDialog(mapping) {
        const isOwn = mapping.is_own;
        
        const html = `
            <div class="sheet-drag-indicator"></div>
            <div class="sheet-header">
                <h2 style="margin: 0; font-size: 24px; font-weight: 700;">Zuordnung bearbeiten</h2>
                <div class="sheet-close-btn" onclick="closeSheet('editMappingSheet')">
                    <i data-lucide="x"></i>
                </div>
            </div>
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; font-weight: 600; font-size: 14px; color: var(--text-sec);">
                    Ordnername (z.B. "Ph", "GdT")
                </label>
                <input type="text" id="edit-informal-name" class="ios-input" 
                       value="${this.escapeHtml(mapping.informal_name)}" 
                       ${!isOwn ? 'disabled' : ''}>
            </div>
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; font-weight: 600; font-size: 14px; color: var(--text-sec);">
                    Offizielles Fach
                </label>
                <select id="edit-subject-id" class="ios-input" ${!isOwn ? 'disabled' : ''}>
                    ${this.subjects.map(s => `
                        <option value="${s.id}" ${s.id === mapping.subject_id ? 'selected' : ''}>
                            ${this.escapeHtml(s.name)}
                        </option>
                    `).join('')}
                </select>
            </div>
            ${isOwn ? `
                <button class="ios-btn" onclick="subjectMappingManager.saveEdit(${mapping.id})">
                    Speichern
                </button>
                <button class="ios-btn btn-danger-light" onclick="subjectMappingManager.confirmDelete(${mapping.id})">
                    Löschen
                </button>
            ` : `
                <p style="color: var(--text-sec); font-size: 14px; text-align: center; padding: 20px;">
                    Diese Zuordnung wurde ${mapping.is_global ? 'global' : 'von einem anderen Benutzer'} erstellt und kann nicht bearbeitet werden.
                </p>
            `}
        `;

        const sheet = document.getElementById('editMappingSheet');
        if (sheet) {
            sheet.innerHTML = html;
            if (typeof lucide !== 'undefined') lucide.createIcons();
            openSheet('editMappingSheet');
        }
    }

    async saveEdit(id) {
        const informalName = document.getElementById('edit-informal-name').value.trim();
        const subjectId = parseInt(document.getElementById('edit-subject-id').value);

        if (!informalName) {
            alert('Bitte gib einen Ordnernamen ein');
            return;
        }

        try {
            await this.updateMapping(id, {
                informal_name: informalName,
                subject_id: subjectId
            });
            closeSheet('editMappingSheet');
            this.renderMappingsList('mappings-list');
            showToast('Zuordnung aktualisiert');
        } catch (error) {
            alert('Fehler beim Aktualisieren: ' + error.message);
        }
    }

    confirmDelete(id) {
        if (confirm('Möchtest du diese Zuordnung wirklich löschen?')) {
            this.deleteMapping(id).then(() => {
                closeSheet('editMappingSheet');
                this.renderMappingsList('mappings-list');
                showToast('Zuordnung gelöscht');
            }).catch(error => {
                alert('Fehler beim Löschen: ' + error.message);
            });
        }
    }

    showCreateDialog() {
        const html = `
            <div class="sheet-drag-indicator"></div>
            <div class="sheet-header">
                <h2 style="margin: 0; font-size: 24px; font-weight: 700;">Neue Zuordnung</h2>
                <div class="sheet-close-btn" onclick="closeSheet('createMappingSheet')">
                    <i data-lucide="x"></i>
                </div>
            </div>
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; font-weight: 600; font-size: 14px; color: var(--text-sec);">
                    Ordnername (z.B. "Ph", "GdT", "Technik")
                </label>
                <input type="text" id="new-informal-name" class="ios-input" 
                       placeholder="Abkürzung oder informeller Name">
            </div>
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; font-weight: 600; font-size: 14px; color: var(--text-sec);">
                    Offizielles Fach
                </label>
                <select id="new-subject-id" class="ios-input">
                    <option value="">Fach auswählen...</option>
                    ${this.subjects.map(s => `
                        <option value="${s.id}">${this.escapeHtml(s.name)}</option>
                    `).join('')}
                </select>
            </div>
            <button class="ios-btn" onclick="subjectMappingManager.createNew()">
                Erstellen
            </button>
        `;

        const sheet = document.getElementById('createMappingSheet');
        if (sheet) {
            sheet.innerHTML = html;
            if (typeof lucide !== 'undefined') lucide.createIcons();
            openSheet('createMappingSheet');
        }
    }

    async createNew() {
        const informalName = document.getElementById('new-informal-name').value.trim();
        const subjectId = parseInt(document.getElementById('new-subject-id').value);

        if (!informalName) {
            alert('Bitte gib einen Ordnernamen ein');
            return;
        }

        if (!subjectId) {
            alert('Bitte wähle ein Fach aus');
            return;
        }

        try {
            await this.createMapping(informalName, subjectId);
            closeSheet('createMappingSheet');
            this.renderMappingsList('mappings-list');
            showToast('Zuordnung erstellt');
        } catch (error) {
            alert('Fehler beim Erstellen: ' + error.message);
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize global instance
let subjectMappingManager;

// Helper functions for toast notifications
function showToast(message) {
    // Simple toast implementation
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 120px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--card-bg);
        backdrop-filter: var(--glass-blur);
        padding: 12px 24px;
        border-radius: 20px;
        box-shadow: var(--shadow);
        z-index: 3000;
        animation: slideUp 0.3s ease;
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}
