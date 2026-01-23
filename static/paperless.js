/* 
 * Paperless-NGX Integration für L8teStudy
 * Ersetzt die alte Google Drive Integration
 */

let activePaperlessTab = 'documents';
let paperlessConfig = null;
let paperlessTags = [];
let paperlessCorrespondents = [];
let paperlessDocumentTypes = [];
let currentPaperlessPage = 1;
let paperlessFilters = {
    query: '',
    tags: [],
    correspondent: null,
    document_type: null
};

// --- Main Render Function ---

async function renderPaperless(tab = 'documents') {
    currentView = 'drive'; // Keep same view name for navigation compatibility
    activePaperlessTab = tab;
    setPageTitle('Dokumente (Paperless)');

    const container = document.getElementById('app-container');

    // Check if Paperless is configured
    const configStatus = await checkPaperlessConfig();

    if (!configStatus.configured) {
        container.innerHTML = renderPaperlessSetup();
        lucide.createIcons();
        return;
    }

    paperlessConfig = configStatus;

    container.innerHTML = `
        <div class="controls-row">
            <div class="tab-bar">
                <button class="tab-btn ${tab === 'documents' ? 'active' : ''}" onclick="renderPaperless('documents')">
                    <i data-lucide="file-text" style="width:16px; margin-right:6px;"></i>
                    Dokumente
                </button>
                <button class="tab-btn ${tab === 'upload' ? 'active' : ''}" onclick="renderPaperless('upload')">
                    <i data-lucide="upload" style="width:16px; margin-right:6px;"></i>
                    Hochladen
                </button>
            </div>
            <button class="btn-chat-open" style="width:36px; height:36px; padding:0;" onclick="showPaperlessSettings()" title="Einstellungen">
                <i data-lucide="settings" style="width:18px;"></i>
            </button>
        </div>
        
        ${tab === 'documents' ? await renderPaperlessDocuments() : renderPaperlessUpload()}
    `;

    lucide.createIcons();
}

// --- Configuration Check ---

async function checkPaperlessConfig() {
    try {
        const res = await fetch('/api/paperless/config');
        return await res.json();
    } catch (e) {
        console.error('Error checking Paperless config:', e);
        return { configured: false };
    }
}

// --- Setup Screen ---

function renderPaperlessSetup() {
    return `
        <div class="floating-card" style="text-align:center; padding:50px 30px; max-width:500px; margin:40px auto;">
            <div style="font-size: 64px; margin-bottom: 25px;">
                <i data-lucide="file-box" style="width:80px; height:80px; color:var(--accent); opacity:0.3;"></i>
            </div>
            <h2 style="font-size:24px; margin-bottom:15px; font-weight:700;">Paperless-NGX Integration</h2>
            <p class="item-sub" style="margin-bottom:30px; line-height:1.6;">
                Verbinde L8teStudy mit deiner Paperless-NGX Instanz für intelligentes Dokumenten-Management 
                mit OCR, automatischem Tagging und Volltextsuche.
            </p>
            
            <div style="background:var(--tab-bg); border-radius:16px; padding:20px; margin-bottom:25px; text-align:left;">
                <div style="font-weight:600; margin-bottom:12px; display:flex; align-items:center; gap:8px;">
                    <i data-lucide="check-circle" style="width:18px; color:var(--success);"></i>
                    Features
                </div>
                <ul style="list-style:none; padding:0; margin:0; color:var(--text-sec); font-size:14px; line-height:2;">
                    <li>✨ OCR - Automatische Texterkennung</li>
                    <li>🔍 Volltextsuche in allen Dokumenten</li>
                    <li>🏷️ Intelligentes Tagging-System</li>
                    <li>📊 Dokumenttypen & Korrespondenten</li>
                    <li>🔒 Selbst-gehostet & DSGVO-konform</li>
                </ul>
            </div>
            
            <button class="ios-btn" style="width:100%; max-width:300px; padding:14px; font-size:16px;" onclick="showPaperlessSettings()">
                <i data-lucide="settings" style="width:18px; margin-right:8px;"></i>
                Jetzt konfigurieren
            </button>
            
            <p class="item-sub" style="margin-top:20px; font-size:12px;">
                <a href="/PAPERLESS_INTEGRATION_README.md" target="_blank" style="color:var(--accent);">
                    📖 Setup-Anleitung anzeigen
                </a>
            </p>
        </div>
    `;
}

// --- Settings Modal ---

async function showPaperlessSettings() {
    const config = await checkPaperlessConfig();

    const html = `
        <div style="padding:0 5px;">
            <h2 style="font-size:22px; margin-bottom:20px; font-weight:700;">
                <i data-lucide="settings" style="width:24px; margin-right:8px; vertical-align:middle;"></i>
                Paperless Einstellungen
            </h2>
            
            <form id="paperless-config-form" onsubmit="savePaperlessConfig(event)">
                <div class="form-group" style="margin-bottom:20px;">
                    <label style="display:block; margin-bottom:8px; font-weight:600; font-size:14px;">
                        Paperless URL
                    </label>
                    <input 
                        type="url" 
                        id="paperless-url" 
                        class="ios-input" 
                        placeholder="https://paperless.example.com" 
                        value="${config.url || ''}"
                        required
                        style="width:100%;"
                    >
                    <small class="item-sub" style="display:block; margin-top:6px; font-size:12px;">
                        Die URL deiner Paperless-NGX Instanz (ohne trailing slash)
                    </small>
                </div>
                
                <div class="form-group" style="margin-bottom:20px;">
                    <label style="display:block; margin-bottom:8px; font-weight:600; font-size:14px;">
                        API Token
                    </label>
                    <input 
                        type="password" 
                        id="paperless-token" 
                        class="ios-input" 
                        placeholder="Token hier eingeben" 
                        ${config.configured ? 'placeholder="••••••••••••••••"' : ''}
                        style="width:100%; font-family: monospace;"
                    >
                    <small class="item-sub" style="display:block; margin-top:6px; font-size:12px;">
                        API Token aus Paperless-NGX Einstellungen → API Tokens
                    </small>
                </div>
                
                ${window.currentUser.is_admin || window.currentUser.is_super_admin ? `
                <div class="form-group" style="margin-bottom:20px;">
                    <label style="display:block; margin-bottom:8px; font-weight:600; font-size:14px;">
                        Gültigkeitsbereich
                    </label>
                    <select id="paperless-scope" class="ios-input" style="width:100%;">
                        <option value="user">Nur für mich</option>
                        ${window.currentUser.is_admin ? '<option value="class">Für meine Klasse</option>' : ''}
                        ${window.currentUser.is_super_admin ? '<option value="global">Global (alle Klassen)</option>' : ''}
                    </select>
                </div>
                ` : ''}
                
                <div class="form-group" style="margin-bottom:25px;">
                    <label style="display:flex; align-items:center; gap:10px; cursor:pointer;">
                        <input type="checkbox" id="paperless-auto-sync" ${config.auto_sync !== false ? 'checked' : ''}>
                        <span style="font-weight:600; font-size:14px;">Automatische Synchronisation</span>
                    </label>
                </div>
                
                <div id="connection-status" style="margin-bottom:20px;"></div>
                
                <div style="display:flex; gap:10px;">
                    <button type="button" class="ios-btn btn-sec" style="flex:1;" onclick="testPaperlessConnection()">
                        <i data-lucide="wifi" style="width:16px; margin-right:6px;"></i>
                        Verbindung testen
                    </button>
                    <button type="submit" class="ios-btn" style="flex:1;">
                        <i data-lucide="save" style="width:16px; margin-right:6px;"></i>
                        Speichern
                    </button>
                </div>
            </form>
            
            ${config.configured && config.last_sync ? `
                <div style="margin-top:20px; padding:15px; background:var(--tab-bg); border-radius:12px; font-size:13px; color:var(--text-sec);">
                    <i data-lucide="clock" style="width:14px; margin-right:6px;"></i>
                    Letzte Synchronisation: ${new Date(config.last_sync).toLocaleString('de-DE')}
                </div>
            ` : ''}
        </div>
    `;

    openSheet(html);
}

async function testPaperlessConnection() {
    const url = document.getElementById('paperless-url').value.trim();
    const token = document.getElementById('paperless-token').value.trim();
    const statusDiv = document.getElementById('connection-status');

    if (!url || !token) {
        statusDiv.innerHTML = `
            <div style="padding:12px; background:rgba(255,59,48,0.1); border-radius:10px; color:var(--danger); font-size:14px;">
                <i data-lucide="alert-circle" style="width:16px; margin-right:6px;"></i>
                Bitte URL und Token eingeben
            </div>
        `;
        lucide.createIcons();
        return;
    }

    statusDiv.innerHTML = `
        <div style="padding:12px; background:var(--tab-bg); border-radius:10px; font-size:14px;">
            <i data-lucide="loader-2" class="spin" style="width:16px; margin-right:6px;"></i>
            Teste Verbindung...
        </div>
    `;
    lucide.createIcons();

    try {
        const res = await fetch('/api/paperless/config/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, token })
        });

        const result = await res.json();

        if (result.success) {
            statusDiv.innerHTML = `
                <div style="padding:12px; background:rgba(52,199,89,0.1); border-radius:10px; color:var(--success); font-size:14px;">
                    <i data-lucide="check-circle" style="width:16px; margin-right:6px;"></i>
                    Verbindung erfolgreich! ${result.user ? `Angemeldet als: ${result.user.username || 'Benutzer'}` : ''}
                </div>
            `;
        } else {
            statusDiv.innerHTML = `
                <div style="padding:12px; background:rgba(255,59,48,0.1); border-radius:10px; color:var(--danger); font-size:14px;">
                    <i data-lucide="x-circle" style="width:16px; margin-right:6px;"></i>
                    ${result.message || 'Verbindung fehlgeschlagen'}
                </div>
            `;
        }
    } catch (e) {
        statusDiv.innerHTML = `
            <div style="padding:12px; background:rgba(255,59,48,0.1); border-radius:10px; color:var(--danger); font-size:14px;">
                <i data-lucide="x-circle" style="width:16px; margin-right:6px;"></i>
                Fehler: ${e.message}
            </div>
        `;
    }

    lucide.createIcons();
}

async function savePaperlessConfig(event) {
    event.preventDefault();

    const url = document.getElementById('paperless-url').value.trim();
    const token = document.getElementById('paperless-token').value.trim();
    const scope = document.getElementById('paperless-scope')?.value || 'user';
    const autoSync = document.getElementById('paperless-auto-sync').checked;

    if (!url) {
        showToast('Bitte URL eingeben', 'error');
        return;
    }

    // If token field is empty and we're editing existing config, don't update token
    const data = {
        url,
        scope,
        auto_sync: autoSync
    };

    if (token) {
        data.token = token;
    }

    try {
        const res = await fetch('/api/paperless/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        if (result.success) {
            showToast('Konfiguration gespeichert!', 'success');
            closeSheet();
            renderPaperless();
        } else {
            showToast(result.message || 'Fehler beim Speichern', 'error');
        }
    } catch (e) {
        showToast('Fehler: ' + e.message, 'error');
    }
}

// --- Documents View ---

async function renderPaperlessDocuments() {
    // Load tags and correspondents for filters
    await loadPaperlessMetadata();

    return `
        <div class="floating-card" style="margin-bottom:20px; padding:16px;">
            <div style="display:flex; gap:10px; margin-bottom:12px; flex-wrap:wrap;">
                <div class="search-container active" style="flex:1; min-width:200px; box-shadow:none; border:none; background:var(--tab-bg); height:40px;">
                    <div class="search-icon-box" style="min-width:40px; height:40px;">
                        <i data-lucide="search" style="width:18px"></i>
                    </div>
                    <input 
                        type="text" 
                        id="paperless-search-input" 
                        class="search-input" 
                        style="opacity:1; transform:none; font-size:15px;" 
                        placeholder="Dokumente durchsuchen..." 
                        onkeyup="handlePaperlessSearch(event)"
                        value="${paperlessFilters.query}"
                    >
                </div>
                <button class="btn-chat-open" style="width:40px; height:40px; padding:0;" onclick="syncPaperlessDocuments()" title="Synchronisieren">
                    <i data-lucide="refresh-cw" style="width:18px;"></i>
                </button>
            </div>
            
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                <select id="paperless-tag-filter" class="ios-input" style="flex:1; min-width:150px; font-size:13px;" onchange="applyPaperlessFilters()">
                    <option value="">Alle Tags</option>
                    ${paperlessTags.map(tag => `
                        <option value="${tag.id}" ${paperlessFilters.tags.includes(tag.id) ? 'selected' : ''}>
                            ${tag.name}
                        </option>
                    `).join('')}
                </select>
                
                <select id="paperless-correspondent-filter" class="ios-input" style="flex:1; min-width:150px; font-size:13px;" onchange="applyPaperlessFilters()">
                    <option value="">Alle Korrespondenten</option>
                    ${paperlessCorrespondents.map(corr => `
                        <option value="${corr.id}" ${paperlessFilters.correspondent === corr.id ? 'selected' : ''}>
                            ${corr.name}
                        </option>
                    `).join('')}
                </select>
            </div>
        </div>
        
        <div id="paperless-documents-container">
            <div style="text-align:center; padding:40px; color:var(--text-sec)">
                <div class="spinner-icon" style="margin-bottom:10px;">
                    <i data-lucide="loader-2" class="spin" style="width:24px;"></i>
                </div>
                Lade Dokumente...
            </div>
        </div>
    `;
}

async function loadPaperlessMetadata() {
    try {
        const [tagsRes, corrsRes] = await Promise.all([
            fetch('/api/paperless/tags'),
            fetch('/api/paperless/correspondents')
        ]);

        paperlessTags = await tagsRes.json();
        paperlessCorrespondents = await corrsRes.json();
    } catch (e) {
        console.error('Error loading metadata:', e);
    }
}

async function loadPaperlessDocuments() {
    const container = document.getElementById('paperless-documents-container');

    try {
        const params = new URLSearchParams({
            page: currentPaperlessPage,
            page_size: 25
        });

        if (paperlessFilters.query) params.append('query', paperlessFilters.query);
        if (paperlessFilters.tags.length > 0) params.append('tags', paperlessFilters.tags.join(','));
        if (paperlessFilters.correspondent) params.append('correspondent', paperlessFilters.correspondent);

        const res = await fetch(`/api/paperless/documents?${params}`);
        const data = await res.json();

        if (data.results && data.results.length === 0) {
            container.innerHTML = `
                <div class="floating-card" style="text-align:center; padding:50px 30px;">
                    <div style="font-size:48px; margin-bottom:20px; opacity:0.15;">
                        <i data-lucide="inbox" style="width:72px; height:72px;"></i>
                    </div>
                    <h3 style="font-size:18px; margin-bottom:10px; font-weight:600;">Keine Dokumente gefunden</h3>
                    <p class="item-sub">Lade dein erstes Dokument hoch!</p>
                </div>
            `;
            lucide.createIcons();
            return;
        }

        container.innerHTML = data.results.map((doc, idx) => `
            <div class="floating-card slide-in-bottom" style="padding:18px; margin-bottom:12px; cursor:pointer; animation-delay:${idx * 0.03}s; animation-fill-mode:both;" onclick="viewPaperlessDocument(${doc.id})">
                <div style="display:flex; gap:14px; align-items:start;">
                    <div style="position:relative; flex-shrink:0;">
                        <img 
                            src="/api/paperless/documents/${doc.id}/preview" 
                            style="width:60px; height:80px; object-fit:cover; border-radius:8px; background:var(--tab-bg);"
                            onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
                        >
                        <div style="display:none; width:60px; height:80px; background:var(--tab-bg); border-radius:8px; align-items:center; justify-content:center;">
                            <i data-lucide="file-text" style="width:24px; color:var(--text-sec);"></i>
                        </div>
                    </div>
                    <div style="flex:1; min-width:0;">
                        <div class="item-title" style="font-size:16px; margin-bottom:6px;">${doc.title || doc.original_file_name || 'Unbenannt'}</div>
                        <div class="item-sub" style="font-size:13px; margin-bottom:8px;">
                            <i data-lucide="calendar" style="width:12px; margin-right:4px;"></i>
                            ${new Date(doc.created).toLocaleDateString('de-DE')}
                            ${doc.correspondent__name ? `• <i data-lucide="user" style="width:12px; margin-left:6px; margin-right:4px;"></i>${doc.correspondent__name}` : ''}
                        </div>
                        ${doc.tags && doc.tags.length > 0 ? `
                            <div style="display:flex; gap:6px; flex-wrap:wrap; margin-top:8px;">
                                ${doc.tags.map(tagId => {
            const tag = paperlessTags.find(t => t.id === tagId);
            return tag ? `
                                        <span style="font-size:11px; padding:4px 10px; background:${tag.color}20; color:${tag.color}; border-radius:6px; font-weight:600;">
                                            ${tag.name}
                                        </span>
                                    ` : '';
        }).join('')}
                            </div>
                        ` : ''}
                    </div>
                    <div style="display:flex; gap:6px;" onclick="event.stopPropagation();">
                        <button class="btn-chat-open" style="width:36px; height:36px; padding:0;" onclick="downloadPaperlessDocument(${doc.id})" title="Herunterladen">
                            <i data-lucide="download" style="width:16px;"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        // Pagination
        if (data.count > 25) {
            const totalPages = Math.ceil(data.count / 25);
            container.innerHTML += `
                <div style="display:flex; justify-content:center; gap:10px; margin-top:20px; padding:20px;">
                    <button class="ios-btn btn-sec btn-small" ${currentPaperlessPage === 1 ? 'disabled' : ''} onclick="changePaperlessPage(${currentPaperlessPage - 1})">
                        <i data-lucide="chevron-left" style="width:16px;"></i>
                    </button>
                    <span style="padding:8px 16px; color:var(--text-sec);">Seite ${currentPaperlessPage} von ${totalPages}</span>
                    <button class="ios-btn btn-sec btn-small" ${currentPaperlessPage === totalPages ? 'disabled' : ''} onclick="changePaperlessPage(${currentPaperlessPage + 1})">
                        <i data-lucide="chevron-right" style="width:16px;"></i>
                    </button>
                </div>
            `;
        }

        lucide.createIcons();
    } catch (e) {
        console.error('Error loading documents:', e);
        container.innerHTML = `
            <div class="floating-card" style="text-align:center; padding:40px;">
                <p class="item-sub" style="color:var(--danger);">Fehler beim Laden der Dokumente</p>
            </div>
        `;
    }
}

function changePaperlessPage(page) {
    currentPaperlessPage = page;
    loadPaperlessDocuments();
}

async function handlePaperlessSearch(e) {
    if (e.key === 'Enter') {
        paperlessFilters.query = e.target.value.trim();
        currentPaperlessPage = 1;
        await loadPaperlessDocuments();
    }
}

async function applyPaperlessFilters() {
    const tagFilter = document.getElementById('paperless-tag-filter').value;
    const corrFilter = document.getElementById('paperless-correspondent-filter').value;

    paperlessFilters.tags = tagFilter ? [parseInt(tagFilter)] : [];
    paperlessFilters.correspondent = corrFilter ? parseInt(corrFilter) : null;
    currentPaperlessPage = 1;

    await loadPaperlessDocuments();
}

async function syncPaperlessDocuments() {
    showToast('Synchronisiere...', 'info');

    try {
        const res = await fetch('/api/paperless/sync', { method: 'POST' });
        const result = await res.json();

        if (result.success) {
            showToast(`${result.documents_synced} Dokumente synchronisiert!`, 'success');
            await loadPaperlessDocuments();
        } else {
            showToast(result.message || 'Sync fehlgeschlagen', 'error');
        }
    } catch (e) {
        showToast('Fehler: ' + e.message, 'error');
    }
}

// --- Upload View ---

function renderPaperlessUpload() {
    return `
        <div class="floating-card" style="max-width:600px; margin:20px auto; padding:30px;">
            <h2 style="font-size:20px; margin-bottom:20px; font-weight:700;">
                <i data-lucide="upload" style="width:22px; margin-right:8px; vertical-align:middle;"></i>
                Dokument hochladen
            </h2>
            
            <form id="paperless-upload-form" onsubmit="uploadToPaperless(event)">
                <div class="form-group" style="margin-bottom:20px;">
                    <label style="display:block; margin-bottom:8px; font-weight:600;">Datei</label>
                    <input 
                        type="file" 
                        id="paperless-file-input" 
                        class="ios-input" 
                        accept=".pdf,.jpg,.jpeg,.png,.gif,.tiff,.txt"
                        required
                        style="width:100%;"
                    >
                </div>
                
                <div class="form-group" style="margin-bottom:20px;">
                    <label style="display:block; margin-bottom:8px; font-weight:600;">Titel (optional)</label>
                    <input 
                        type="text" 
                        id="paperless-title-input" 
                        class="ios-input" 
                        placeholder="Wird automatisch aus Dateinamen generiert"
                        style="width:100%;"
                    >
                </div>
                
                <div class="form-group" style="margin-bottom:20px;">
                    <label style="display:block; margin-bottom:8px; font-weight:600;">Tags (optional)</label>
                    <select id="paperless-tags-input" class="ios-input" multiple style="width:100%; height:100px;">
                        ${paperlessTags.map(tag => `
                            <option value="${tag.id}">${tag.name}</option>
                        `).join('')}
                    </select>
                    <small class="item-sub" style="display:block; margin-top:6px;">Halte Strg/Cmd für Mehrfachauswahl</small>
                </div>
                
                <div class="form-group" style="margin-bottom:20px;">
                    <label style="display:block; margin-bottom:8px; font-weight:600;">Korrespondent (optional)</label>
                    <select id="paperless-correspondent-input" class="ios-input" style="width:100%;">
                        <option value="">Keiner</option>
                        ${paperlessCorrespondents.map(corr => `
                            <option value="${corr.id}">${corr.name}</option>
                        `).join('')}
                    </select>
                </div>
                
                <button type="submit" class="ios-btn" style="width:100%; padding:14px; font-size:16px;">
                    <i data-lucide="upload" style="width:18px; margin-right:8px;"></i>
                    Hochladen
                </button>
            </form>
        </div>
    `;
}

async function uploadToPaperless(event) {
    event.preventDefault();

    const fileInput = document.getElementById('paperless-file-input');
    const titleInput = document.getElementById('paperless-title-input');
    const tagsSelect = document.getElementById('paperless-tags-input');
    const corrSelect = document.getElementById('paperless-correspondent-input');

    if (!fileInput.files[0]) {
        showToast('Bitte Datei auswählen', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    if (titleInput.value.trim()) {
        formData.append('title', titleInput.value.trim());
    }

    const selectedTags = Array.from(tagsSelect.selectedOptions).map(opt => opt.value);
    if (selectedTags.length > 0) {
        formData.append('tags', selectedTags.join(','));
    }

    if (corrSelect.value) {
        formData.append('correspondent', corrSelect.value);
    }

    showToast('Lade hoch...', 'info');

    try {
        const res = await fetch('/api/paperless/documents/upload', {
            method: 'POST',
            body: formData
        });

        const result = await res.json();

        if (result.success) {
            showToast('Dokument hochgeladen! OCR läuft...', 'success');
            fileInput.value = '';
            titleInput.value = '';
            tagsSelect.selectedIndex = -1;
            corrSelect.selectedIndex = 0;

            // Switch to documents tab after 2 seconds
            setTimeout(() => renderPaperless('documents'), 2000);
        } else {
            showToast(result.message || 'Upload fehlgeschlagen', 'error');
        }
    } catch (e) {
        showToast('Fehler: ' + e.message, 'error');
    }
}

// --- Document Details ---

async function viewPaperlessDocument(docId) {
    try {
        const res = await fetch(`/api/paperless/documents/${docId}`);
        const doc = await res.json();

        const html = `
            <div style="padding:0 5px;">
                <h2 style="font-size:20px; margin-bottom:20px; font-weight:700;">
                    ${doc.title || doc.original_file_name || 'Dokument'}
                </h2>
                
                <div style="margin-bottom:20px;">
                    <img 
                        src="/api/paperless/documents/${docId}/preview" 
                        style="width:100%; max-width:400px; border-radius:12px; margin:0 auto; display:block;"
                        onerror="this.style.display='none'"
                    >
                </div>
                
                <div style="background:var(--tab-bg); border-radius:12px; padding:16px; margin-bottom:20px;">
                    <div style="display:grid; grid-template-columns:auto 1fr; gap:12px; font-size:14px;">
                        <span style="color:var(--text-sec);">Erstellt:</span>
                        <span>${new Date(doc.created).toLocaleString('de-DE')}</span>
                        
                        ${doc.correspondent__name ? `
                            <span style="color:var(--text-sec);">Korrespondent:</span>
                            <span>${doc.correspondent__name}</span>
                        ` : ''}
                        
                        ${doc.document_type__name ? `
                            <span style="color:var(--text-sec);">Typ:</span>
                            <span>${doc.document_type__name}</span>
                        ` : ''}
                    </div>
                </div>
                
                ${doc.content ? `
                    <div style="margin-bottom:20px;">
                        <h3 style="font-size:16px; margin-bottom:12px; font-weight:600;">OCR-Text</h3>
                        <div style="background:var(--tab-bg); border-radius:12px; padding:16px; max-height:300px; overflow-y:auto; font-size:13px; line-height:1.6; white-space:pre-wrap;">
                            ${doc.content.substring(0, 1000)}${doc.content.length > 1000 ? '...' : ''}
                        </div>
                    </div>
                ` : ''}
                
                <div style="display:flex; gap:10px;">
                    <button class="ios-btn" style="flex:1;" onclick="downloadPaperlessDocument(${docId}, false)">
                        <i data-lucide="download" style="width:16px; margin-right:6px;"></i>
                        Download (OCR)
                    </button>
                    <button class="ios-btn btn-sec" style="flex:1;" onclick="downloadPaperlessDocument(${docId}, true)">
                        <i data-lucide="file" style="width:16px; margin-right:6px;"></i>
                        Original
                    </button>
                </div>
                
                ${window.currentUser.is_admin || window.currentUser.is_super_admin ? `
                    <button class="ios-btn" style="width:100%; margin-top:10px; background:rgba(255,59,48,0.1); color:var(--danger);" onclick="deletePaperlessDocument(${docId})">
                        <i data-lucide="trash-2" style="width:16px; margin-right:6px;"></i>
                        Löschen
                    </button>
                ` : ''}
            </div>
        `;

        openSheet(html);
    } catch (e) {
        showToast('Fehler beim Laden des Dokuments', 'error');
    }
}

async function downloadPaperlessDocument(docId, original = false) {
    try {
        const url = `/api/paperless/documents/${docId}/download${original ? '?original=true' : ''}`;
        window.open(url, '_blank');
    } catch (e) {
        showToast('Download fehlgeschlagen', 'error');
    }
}

async function deletePaperlessDocument(docId) {
    if (!confirm('Dokument wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden!')) {
        return;
    }

    try {
        const res = await fetch(`/api/paperless/documents/${docId}`, {
            method: 'DELETE'
        });

        const result = await res.json();

        if (result.success) {
            showToast('Dokument gelöscht', 'success');
            closeSheet();
            await loadPaperlessDocuments();
        } else {
            showToast('Löschen fehlgeschlagen', 'error');
        }
    } catch (e) {
        showToast('Fehler: ' + e.message, 'error');
    }
}

// Initialize when documents tab is rendered
document.addEventListener('DOMContentLoaded', () => {
    // Auto-load documents when container exists
    const observer = new MutationObserver(() => {
        const container = document.getElementById('paperless-documents-container');
        if (container && container.innerHTML.includes('Lade Dokumente')) {
            loadPaperlessDocuments();
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
});
