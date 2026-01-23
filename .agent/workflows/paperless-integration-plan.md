---
description: L8teStudy Paperless-NGX Integration - Implementierungsplan
---

# Paperless-NGX Integration für L8teStudy

## Überblick
Ersetze die komplette Google Drive Integration durch Paperless-NGX Integration. Dateien werden zu Paperless hochgeladen und die Website zeigt diese Dateien an.

## Paperless-NGX API Authentifizierung
Paperless-NGX verwendet **Token-basierte Authentifizierung**:
- API Token wird in den Einstellungen von Paperless-NGX generiert
- Token wird im Header gesendet: `Authorization: Token <your-token>`
- Keine OAuth-Flows notwendig

## Implementierungsschritte

### Phase 1: Vorbereitung & Cleanup (Google Drive entfernen)

#### 1.1 Datenbank-Migration erstellen
- Neue Tabellen für Paperless-Integration:
  - `paperless_config`: Speichert Paperless-URL und API-Token pro User/Klasse
  - `paperless_document`: Cached Paperless-Dokumente lokal
  - `paperless_tag`: Tags aus Paperless
  - `paperless_correspondent`: Korrespondenten aus Paperless
  
- Alte Drive-Tabellen für Entfernung markieren:
  - `drive_folder`
  - `drive_file`
  - `drive_file_content`

#### 1.2 Backend-Dateien entfernen/ersetzen
- **Löschen:**
  - `app/drive_sync.py` (Google Drive Sync)
  - `app/drive_search.py` (Google Drive Suche)
  - `init_drive.py` (Google Drive Initialisierung)
  - `DRIVE_INTEGRATION_README.md`

- **Erstellen:**
  - `app/paperless_client.py` (Paperless API Client)
  - `app/paperless_sync.py` (Paperless Sync Service)
  - `PAPERLESS_INTEGRATION_README.md`

#### 1.3 Models aktualisieren
- Entfernen: `DriveFolder`, `DriveFile`, `DriveFileContent` aus `app/models.py`
- Hinzufügen: `PaperlessConfig`, `PaperlessDocument`, `PaperlessTag`, `PaperlessCorrespondent`

### Phase 2: Paperless-NGX Backend Implementation

#### 2.1 Paperless API Client erstellen (`app/paperless_client.py`)
```python
class PaperlessClient:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Token {api_token}',
            'Content-Type': 'application/json'
        }
    
    # Methoden:
    - get_documents(page=1, page_size=25, query=None, tags=None)
    - get_document(doc_id)
    - download_document(doc_id, original=False)
    - upload_document(file, title, tags=[], correspondent=None)
    - get_tags()
    - get_correspondents()
    - search_documents(query)
```

#### 2.2 API Routes erstellen (`app/routes.py`)
```python
# Paperless Configuration
@api_bp.route('/paperless/config', methods=['GET', 'POST', 'PUT'])
@login_required
def paperless_config():
    # GET: Aktuelle Konfiguration abrufen
    # POST/PUT: Paperless URL und Token speichern
    pass

# Documents
@api_bp.route('/paperless/documents', methods=['GET'])
@login_required
def get_paperless_documents():
    # Liste aller Dokumente mit Pagination
    pass

@api_bp.route('/paperless/documents/<int:doc_id>', methods=['GET'])
@login_required
def get_paperless_document(doc_id):
    # Einzelnes Dokument Details
    pass

@api_bp.route('/paperless/documents/<int:doc_id>/download', methods=['GET'])
@login_required
def download_paperless_document(doc_id):
    # Dokument herunterladen (Proxy)
    pass

@api_bp.route('/paperless/documents/<int:doc_id>/preview', methods=['GET'])
@login_required
def preview_paperless_document(doc_id):
    # Thumbnail/Preview
    pass

@api_bp.route('/paperless/documents/upload', methods=['POST'])
@login_required
def upload_paperless_document():
    # Neues Dokument hochladen
    pass

@api_bp.route('/paperless/documents/<int:doc_id>', methods=['DELETE'])
@login_required
def delete_paperless_document(doc_id):
    # Dokument löschen
    pass

# Tags & Correspondents
@api_bp.route('/paperless/tags', methods=['GET'])
@login_required
def get_paperless_tags():
    pass

@api_bp.route('/paperless/correspondents', methods=['GET'])
@login_required
def get_paperless_correspondents():
    pass

# Search
@api_bp.route('/paperless/search', methods=['GET'])
@login_required
def search_paperless_documents():
    # Volltextsuche in Paperless
    pass
```

### Phase 3: Frontend Implementation

#### 3.1 Drive-Seite umbauen zu Paperless-Seite
In `templates/index.html`:

**Alte Funktionen entfernen:**
- `renderDriveFolders()`
- `renderDriveFiles()`
- `submitNewDriveFolder()`
- `deleteDriveFolder()`
- `updateDriveFolder()`
- Alle Google Drive OAuth-bezogenen Funktionen

**Neue Funktionen hinzufügen:**
```javascript
// Paperless Configuration
async function showPaperlessSettings()
async function savePaperlessConfig()
async function testPaperlessConnection()

// Document Management
async function renderPaperlessDocuments(page = 1, filters = {})
async function uploadToPaperless(files)
async function downloadFromPaperless(docId)
async function deleteFromPaperless(docId)
async function viewDocumentDetails(docId)

// Search & Filter
async function searchPaperlessDocuments(query)
async function filterByTag(tagId)
async function filterByCorrespondent(corrId)
async function filterByDate(startDate, endDate)

// Tags & Correspondents
async function loadPaperlessTags()
async function loadPaperlessCorrespondents()
```

#### 3.2 UI Design für Paperless-Seite
```html
<div id="paperless-page">
    <!-- Header mit Upload Button -->
    <div class="page-header">
        <h1>Dokumente (Paperless-NGX)</h1>
        <button onclick="showUploadDialog()">+ Hochladen</button>
        <button onclick="showPaperlessSettings()">⚙️ Einstellungen</button>
    </div>
    
    <!-- Filter & Search Bar -->
    <div class="filter-bar">
        <input type="search" placeholder="Suchen..." oninput="searchPaperlessDocuments(this.value)">
        <select onchange="filterByTag(this.value)">
            <option value="">Alle Tags</option>
            <!-- Dynamic tags -->
        </select>
        <select onchange="filterByCorrespondent(this.value)">
            <option value="">Alle Korrespondenten</option>
            <!-- Dynamic correspondents -->
        </select>
    </div>
    
    <!-- Documents Grid/List -->
    <div id="documents-container" class="documents-grid">
        <!-- Dynamic document cards -->
    </div>
    
    <!-- Pagination -->
    <div class="pagination">
        <!-- Page buttons -->
    </div>
</div>
```

#### 3.3 Document Card Design
```html
<div class="document-card">
    <div class="document-thumbnail">
        <img src="/api/paperless/documents/${doc.id}/preview" alt="Preview">
    </div>
    <div class="document-info">
        <h3>${doc.title}</h3>
        <p class="document-date">${doc.created}</p>
        <div class="document-tags">
            ${doc.tags.map(tag => `<span class="tag">${tag.name}</span>`).join('')}
        </div>
        <div class="document-actions">
            <button onclick="downloadFromPaperless(${doc.id})">📥 Download</button>
            <button onclick="viewDocumentDetails(${doc.id})">👁️ Details</button>
            <button onclick="deleteFromPaperless(${doc.id})">🗑️ Löschen</button>
        </div>
    </div>
</div>
```

### Phase 4: Settings & Configuration

#### 4.1 Paperless Settings Dialog
```html
<div id="paperless-settings-modal" class="modal">
    <div class="modal-content">
        <h2>Paperless-NGX Einstellungen</h2>
        
        <div class="form-group">
            <label>Paperless URL</label>
            <input type="url" id="paperless-url" placeholder="https://paperless.example.com">
            <small>Die URL deiner Paperless-NGX Instanz</small>
        </div>
        
        <div class="form-group">
            <label>API Token</label>
            <input type="password" id="paperless-token" placeholder="Token hier eingeben">
            <small>Token aus Paperless-NGX Einstellungen → API Tokens</small>
        </div>
        
        <div class="form-actions">
            <button onclick="testPaperlessConnection()">🔍 Verbindung testen</button>
            <button onclick="savePaperlessConfig()">💾 Speichern</button>
        </div>
        
        <div id="connection-status"></div>
    </div>
</div>
```

#### 4.2 Admin-Bereich erweitern
- Globale Paperless-Konfiguration für die gesamte Schule
- Pro-Klasse oder Pro-User Konfiguration möglich
- Berechtigungen: Wer darf hochladen/löschen?

### Phase 5: Datenbank-Migration

#### 5.1 Migration Script erstellen
```python
# migrations/versions/xxx_add_paperless_remove_drive.py

def upgrade():
    # Neue Paperless Tabellen
    op.create_table('paperless_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('class_id', sa.Integer(), nullable=True),
        sa.Column('paperless_url', sa.String(500), nullable=False),
        sa.Column('api_token', sa.String(500), nullable=False),  # Encrypted
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['class_id'], ['school_class.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('paperless_document',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('paperless_id', sa.Integer(), nullable=False),
        sa.Column('config_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
        sa.Column('correspondent_id', sa.Integer(), nullable=True),
        sa.Column('document_type_id', sa.Integer(), nullable=True),
        sa.Column('cached_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['config_id'], ['paperless_config.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # ... weitere Tabellen
    
    # Alte Drive Tabellen löschen
    op.drop_table('drive_file_content')
    op.drop_table('drive_file')
    op.drop_table('drive_folder')

def downgrade():
    # Rollback falls nötig
    pass
```

### Phase 6: Testing & Documentation

#### 6.1 Tests
- API Client Tests
- Upload/Download Tests
- Search Tests
- Permission Tests

#### 6.2 Dokumentation
- `PAPERLESS_INTEGRATION_README.md` erstellen
- Setup-Anleitung für Paperless-NGX
- API Token Generierung erklären
- Troubleshooting Guide

## Sicherheitsüberlegungen

1. **API Token Verschlüsselung**: Tokens in der DB verschlüsselt speichern
2. **HTTPS**: Paperless-Verbindung nur über HTTPS erlauben
3. **Berechtigungen**: Klare Rollen für Upload/Download/Delete
4. **Rate Limiting**: API-Calls zu Paperless limitieren
5. **Proxy-Downloads**: Dokumente über Backend proxyen, nicht direkt von Paperless

## Vorteile gegenüber Google Drive

✅ Selbst-gehostet - volle Kontrolle
✅ OCR & Volltextsuche eingebaut
✅ Automatische Tagging & Organisation
✅ Keine OAuth-Komplexität
✅ DSGVO-konform
✅ Keine externen Abhängigkeiten
✅ Bessere Integration mit Schul-Workflow

## Nächste Schritte

1. ✅ Plan erstellen (dieser Workflow)
2. ⏳ Phase 1: Google Drive Code entfernen
3. ⏳ Phase 2: Paperless Backend implementieren
4. ⏳ Phase 3: Frontend umbauen
5. ⏳ Phase 4: Settings & Config
6. ⏳ Phase 5: Migration
7. ⏳ Phase 6: Testing & Docs
