// ============================================
// FLASHCARDS MODULE - L8teStudy
// ============================================

let currentDeck = null;
let currentCards = [];
let currentCardIndex = 0;
let isCardFlipped = false;
let studyMode = 'spaced'; // 'spaced' or 'free'
let dueCards = [];

// ============================================
// DECK LIST VIEW
// ============================================

async function renderFlashcardsView() {
    try {
        const response = await fetch('/api/decks');
        const data = await response.json();

        const myDecks = data.my_decks || [];
        const publicDecks = data.public_decks || [];

        let html = `
            <div class="floating-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                    <h2 style="margin:0; font-size:24px; font-weight:700;">${t('my_decks') || 'Meine Decks'}</h2>
                    <button class="ios-btn btn-small" onclick="openCreateDeckSheet()" style="background:var(--accent); color:white;">
                        <i data-lucide="plus" style="width:16px; height:16px;"></i> Neu
                    </button>
                </div>
                ${myDecks.length === 0 ? `
                    <div style="text-align:center; padding:40px 20px; color:var(--text-sec);">
                        <i data-lucide="layers" style="width:48px; height:48px; margin-bottom:16px; opacity:0.3;"></i>
                        <p style="margin:0;">${t('no_decks_yet') || 'Noch keine Decks erstellt'}</p>
                        <p style="margin:8px 0 0 0; font-size:14px;">${t('create_first_deck') || 'Erstelle dein erstes Deck!'}</p>
                    </div>
                ` : myDecks.map(deck => `
                    <div class="list-item" onclick="openDeck(${deck.id})" style="cursor:pointer; padding:16px 0;">
                        <div class="item-content">
                            <div class="item-title">${escapeHtml(deck.title)}</div>
                            <div class="item-sub">
                                ${deck.card_count} ${deck.card_count === 1 ? 'Karte' : 'Karten'}
                                ${deck.is_public ? ' • Öffentlich' : ''}
                            </div>
                        </div>
                        <i data-lucide="chevron-right" style="color:var(--text-sec); width:20px; height:20px;"></i>
                    </div>
                `).join('')}
            </div>
            
            ${publicDecks.length > 0 ? `
                <div class="floating-card">
                    <h2 style="margin:0 0 20px 0; font-size:24px; font-weight:700;">${t('public_decks') || 'Öffentliche Decks'}</h2>
                    ${publicDecks.map(deck => `
                        <div class="list-item" onclick="openDeck(${deck.id})" style="cursor:pointer; padding:16px 0;">
                            <div class="item-content">
                                <div class="item-title">${escapeHtml(deck.title)}</div>
                                <div class="item-sub">
                                    ${deck.card_count} ${deck.card_count === 1 ? 'Karte' : 'Karten'} • ${escapeHtml(deck.author_name)}
                                </div>
                            </div>
                            <i data-lucide="chevron-right" style="color:var(--text-sec); width:20px; height:20px;"></i>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        `;

        document.getElementById('app-container').innerHTML = html;
        lucide.createIcons();

    } catch (error) {
        console.error('Error loading decks:', error);
        showToast('Fehler beim Laden der Decks', 'error');
    }
}

// ============================================
// DECK DETAIL VIEW
// ============================================

async function openDeck(deckId) {
    try {
        const response = await fetch(`/api/decks/${deckId}`);
        const deck = await response.json();

        currentDeck = deck;
        currentCards = deck.cards || [];
        dueCards = currentCards.filter(c => c.is_due);

        previousView = currentView;
        currentView = 'deck-detail';
        updateBackButton();
        updatePageTitle(deck.title);

        const isOwner = deck.is_own;

        let html = `
            <div class="floating-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:20px;">
                    <div>
                        <h2 style="margin:0 0 8px 0; font-size:28px; font-weight:700;">${escapeHtml(deck.title)}</h2>
                        ${deck.description ? `<p style="margin:0; color:var(--text-sec); font-size:15px;">${escapeHtml(deck.description)}</p>` : ''}
                    </div>
                    ${isOwner ? `
                        <button class="ios-btn btn-small btn-sec" onclick="openDeckSettings(${deckId})" style="min-width:auto; padding:8px 12px;">
                            <i data-lucide="settings" style="width:18px; height:18px;"></i>
                        </button>
                    ` : ''}
                </div>
                
                <!-- Stats -->
                <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; margin-bottom:24px;">
                    <div style="background:var(--tab-bg); padding:16px; border-radius:16px; text-align:center;">
                        <div style="font-size:28px; font-weight:700; color:var(--accent);">${deck.stats.new}</div>
                        <div style="font-size:13px; color:var(--text-sec); margin-top:4px;">Neu</div>
                    </div>
                    <div style="background:var(--tab-bg); padding:16px; border-radius:16px; text-align:center;">
                        <div style="font-size:28px; font-weight:700; color:#ff9f0a;">${deck.stats.due}</div>
                        <div style="font-size:13px; color:var(--text-sec); margin-top:4px;">Fällig</div>
                    </div>
                    <div style="background:var(--tab-bg); padding:16px; border-radius:16px; text-align:center;">
                        <div style="font-size:28px; font-weight:700; color:var(--text-main);">${deck.stats.total}</div>
                        <div style="font-size:13px; color:var(--text-sec); margin-top:4px;">Gesamt</div>
                    </div>
                </div>
                
                <!-- Study Buttons -->
                <div style="display:flex; gap:12px; margin-bottom:24px;">
                    <button class="ios-btn" onclick="startStudyMode('spaced')" 
                        style="flex:1; background:var(--accent); color:white; font-size:16px; padding:16px;"
                        ${dueCards.length === 0 ? 'disabled style="opacity:0.5; cursor:not-allowed;"' : ''}>
                        <i data-lucide="brain" style="width:20px; height:20px; margin-right:8px;"></i>
                        Lernen (${dueCards.length})
                    </button>
                    <button class="ios-btn btn-sec" onclick="startStudyMode('free')" 
                        style="flex:1; font-size:16px; padding:16px;"
                        ${currentCards.length === 0 ? 'disabled style="opacity:0.5; cursor:not-allowed;"' : ''}>
                        <i data-lucide="shuffle" style="width:20px; height:20px; margin-right:8px;"></i>
                        Üben
                    </button>
                </div>
                
                ${isOwner ? `
                    <button class="ios-btn btn-sec" onclick="openAddCardSheet(${deckId})" style="width:100%; margin-bottom:20px;">
                        <i data-lucide="plus" style="width:18px; height:18px; margin-right:8px;"></i>
                        Karte hinzufügen
                    </button>
                ` : ''}
            </div>
            
            <!-- Card List -->
            ${currentCards.length > 0 ? `
                <div class="floating-card">
                    <h3 style="margin:0 0 16px 0; font-size:18px; font-weight:600;">Alle Karten</h3>
                    ${currentCards.map((card, idx) => `
                        <div class="list-item" onclick="previewCard(${idx})" style="cursor:pointer; padding:16px 0;">
                            <div class="item-content">
                                <div class="item-title" style="font-size:15px;">${escapeHtml(card.front.substring(0, 60))}${card.front.length > 60 ? '...' : ''}</div>
                                ${card.is_due ? `<div class="item-sub" style="color:#ff9f0a;">● Fällig</div>` : ''}
                            </div>
                            ${isOwner ? `
                                <button class="ios-btn btn-small btn-danger-light" onclick="event.stopPropagation(); deleteCard(${card.id})" style="min-width:auto; padding:6px 12px; margin-left:8px;">
                                    <i data-lucide="trash-2" style="width:16px; height:16px;"></i>
                                </button>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        `;

        document.getElementById('app-container').innerHTML = html;
        lucide.createIcons();

    } catch (error) {
        console.error('Error loading deck:', error);
        showToast('Fehler beim Laden des Decks', 'error');
    }
}

// ============================================
// STUDY MODE
// ============================================

function startStudyMode(mode) {
    studyMode = mode;

    if (mode === 'spaced') {
        currentCards = dueCards;
    } else {
        // Shuffle for free practice
        currentCards = [...currentDeck.cards].sort(() => Math.random() - 0.5);
    }

    if (currentCards.length === 0) {
        showToast('Keine Karten zum Lernen verfügbar', 'info');
        return;
    }

    currentCardIndex = 0;
    isCardFlipped = false;

    previousView = 'deck-detail';
    currentView = 'study';
    updateBackButton();
    updatePageTitle(`${currentDeck.title} - Lernen`);

    // Hide bottom nav, show study nav
    document.querySelector('.bottom-nav').style.display = 'none';
    document.querySelector('.side-nav').style.display = 'none';
    document.getElementById('main-fab').classList.remove('visible');

    if (mode === 'spaced') {
        document.getElementById('study-nav').style.display = 'flex';
        document.getElementById('practice-nav').style.display = 'none';
    } else {
        document.getElementById('study-nav').style.display = 'none';
        document.getElementById('practice-nav').style.display = 'flex';
    }

    renderStudyCard();
}

function renderStudyCard() {
    const card = currentCards[currentCardIndex];
    if (!card) {
        endStudySession();
        return;
    }

    const progress = ((currentCardIndex + 1) / currentCards.length * 100).toFixed(0);

    let html = `
        <div class="floating-card" style="margin-top:20px; min-height:60vh;">
            <!-- Progress -->
            <div style="margin-bottom:24px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="font-size:14px; font-weight:600; color:var(--text-sec);">
                        ${currentCardIndex + 1} / ${currentCards.length}
                    </span>
                    <span style="font-size:14px; font-weight:600; color:var(--accent);">${progress}%</span>
                </div>
                <div style="height:6px; background:var(--tab-bg); border-radius:10px; overflow:hidden;">
                    <div style="height:100%; background:var(--accent); width:${progress}%; transition:width 0.3s ease;"></div>
                </div>
            </div>
            
            <!-- Card -->
            <div class="flashcard-container" onclick="flipCard()" style="cursor:pointer;">
                <div class="flashcard ${isCardFlipped ? 'flipped' : ''}" id="study-card">
                    <div class="flashcard-front">
                        <div style="position:absolute; top:16px; left:16px; font-size:12px; font-weight:600; color:var(--text-sec); text-transform:uppercase;">
                            Frage
                        </div>
                        <div class="flashcard-content">
                            ${escapeHtml(card.front)}
                        </div>
                        <div style="position:absolute; bottom:16px; right:16px; color:var(--text-sec); opacity:0.5;">
                            <i data-lucide="rotate-cw" style="width:20px; height:20px;"></i>
                        </div>
                    </div>
                    <div class="flashcard-back">
                        <div style="position:absolute; top:16px; left:16px; font-size:12px; font-weight:600; color:var(--text-sec); text-transform:uppercase;">
                            Antwort
                        </div>
                        <div class="flashcard-content">
                            ${escapeHtml(card.back)}
                        </div>
                    </div>
                </div>
            </div>
            
            ${!isCardFlipped ? `
                <div style="text-align:center; margin-top:24px; color:var(--text-sec); font-size:14px;">
                    <i data-lucide="hand-metal" style="width:18px; height:18px; vertical-align:middle; margin-right:4px;"></i>
                    Tippe zum Umdrehen
                </div>
            ` : ''}
        </div>
    `;

    document.getElementById('app-container').innerHTML = html;
    lucide.createIcons();
}

function flipCard() {
    isCardFlipped = !isCardFlipped;
    const cardEl = document.getElementById('study-card');
    if (cardEl) {
        cardEl.classList.toggle('flipped');
    }
}

async function rateCard(quality) {
    if (!isCardFlipped) {
        showToast('Bitte drehe die Karte zuerst um', 'info');
        return;
    }

    const card = currentCards[currentCardIndex];

    if (studyMode === 'spaced') {
        try {
            // Map UI ratings to SM-2 quality (0-5)
            // 1=Again -> 1, 2=Hard -> 2, 3=Good -> 4, 4=Easy -> 5
            const qualityMap = { 1: 1, 2: 2, 3: 4, 4: 5 };
            const sm2Quality = qualityMap[quality];

            await fetch(`/api/cards/${card.id}/review`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ quality: sm2Quality })
            });
        } catch (error) {
            console.error('Error rating card:', error);
        }
    }

    // Next card
    currentCardIndex++;
    isCardFlipped = false;

    if (currentCardIndex >= currentCards.length) {
        endStudySession();
    } else {
        renderStudyCard();
    }
}

function nextFreePracticeCard() {
    currentCardIndex++;
    isCardFlipped = false;

    if (currentCardIndex >= currentCards.length) {
        endStudySession();
    } else {
        renderStudyCard();
    }
}

function endStudySession() {
    showToast('🎉 Lernsession abgeschlossen!', 'success');

    // Reset UI
    document.querySelector('.bottom-nav').style.display = 'flex';
    document.querySelector('.side-nav').style.display = 'flex';
    document.getElementById('study-nav').style.display = 'none';
    document.getElementById('practice-nav').style.display = 'none';

    // Return to deck
    openDeck(currentDeck.id);
}

// ============================================
// CARD PREVIEW
// ============================================

function previewCard(index) {
    const card = currentCards[index];

    openSheet(`
        <div class="sheet-header">
            <h3 style="margin:0; font-size:20px; font-weight:700;">Kartenvorschau</h3>
            <div class="sheet-close-btn" onclick="closeSheet()">
                <i data-lucide="x"></i>
            </div>
        </div>
        
        <div style="margin-bottom:20px;">
            <label style="display:block; font-size:13px; font-weight:600; color:var(--text-sec); margin-bottom:8px; text-transform:uppercase;">
                Vorderseite
            </label>
            <div style="background:var(--tab-bg); padding:16px; border-radius:12px; min-height:80px; font-size:16px;">
                ${escapeHtml(card.front)}
            </div>
        </div>
        
        <div>
            <label style="display:block; font-size:13px; font-weight:600; color:var(--text-sec); margin-bottom:8px; text-transform:uppercase;">
                Rückseite
            </label>
            <div style="background:var(--tab-bg); padding:16px; border-radius:12px; min-height:80px; font-size:16px;">
                ${escapeHtml(card.back)}
            </div>
        </div>
    `);

    lucide.createIcons();
}

// ============================================
// CREATE/EDIT DECK
// ============================================

function openCreateDeckSheet() {
    openSheet(`
        <div class="sheet-header">
            <h3 style="margin:0; font-size:20px; font-weight:700;">Neues Deck erstellen</h3>
            <div class="sheet-close-btn" onclick="closeSheet()">
                <i data-lucide="x"></i>
            </div>
        </div>
        
        <input type="text" id="deck-title" class="ios-input" placeholder="Deck-Titel" required>
        <textarea id="deck-description" class="ios-input" placeholder="Beschreibung (optional)" rows="3"></textarea>
        
        <div style="display:flex; align-items:center; justify-content:space-between; padding:16px; background:var(--tab-bg); border-radius:12px; margin-bottom:15px;">
            <span style="font-weight:600;">Öffentlich teilen</span>
            <div class="ios-toggle" id="deck-public-toggle" onclick="this.classList.toggle('active')">
                <div class="ios-toggle-knob"></div>
            </div>
        </div>
        
        <button class="ios-btn" onclick="createDeck()">Deck erstellen</button>
    `);

    lucide.createIcons();
}

async function createDeck() {
    const title = document.getElementById('deck-title').value.trim();
    const description = document.getElementById('deck-description').value.trim();
    const isPublic = document.getElementById('deck-public-toggle').classList.contains('active');

    if (!title) {
        showToast('Bitte gib einen Titel ein', 'error');
        return;
    }

    try {
        const response = await fetch('/api/decks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, is_public: isPublic })
        });

        const data = await response.json();

        if (data.success) {
            showToast('Deck erstellt!', 'success');
            closeSheet();
            openDeck(data.id);
        } else {
            showToast(data.error || 'Fehler beim Erstellen', 'error');
        }
    } catch (error) {
        console.error('Error creating deck:', error);
        showToast('Fehler beim Erstellen', 'error');
    }
}

// ============================================
// ADD CARD
// ============================================

function openAddCardSheet(deckId) {
    openSheet(`
        <div class="sheet-header">
            <h3 style="margin:0; font-size:20px; font-weight:700;">Neue Karte hinzufügen</h3>
            <div class="sheet-close-btn" onclick="closeSheet()">
                <i data-lucide="x"></i>
            </div>
        </div>
        
        <label style="display:block; font-size:13px; font-weight:600; color:var(--text-sec); margin-bottom:8px;">
            Vorderseite (Frage)
        </label>
        <textarea id="card-front" class="ios-input" placeholder="Was möchtest du lernen?" rows="4" required></textarea>
        
        <label style="display:block; font-size:13px; font-weight:600; color:var(--text-sec); margin-bottom:8px;">
            Rückseite (Antwort)
        </label>
        <textarea id="card-back" class="ios-input" placeholder="Die Antwort..." rows="4" required></textarea>
        
        <button class="ios-btn" onclick="addCard(${deckId})">Karte hinzufügen</button>
    `);

    lucide.createIcons();
}

async function addCard(deckId) {
    const front = document.getElementById('card-front').value.trim();
    const back = document.getElementById('card-back').value.trim();

    if (!front || !back) {
        showToast('Bitte fülle beide Seiten aus', 'error');
        return;
    }

    try {
        const response = await fetch(`/api/decks/${deckId}/cards`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ front, back })
        });

        const data = await response.json();

        if (data.success) {
            showToast('Karte hinzugefügt!', 'success');
            closeSheet();
            openDeck(deckId);
        } else {
            showToast(data.error || 'Fehler beim Hinzufügen', 'error');
        }
    } catch (error) {
        console.error('Error adding card:', error);
        showToast('Fehler beim Hinzufügen', 'error');
    }
}

// ============================================
// DELETE CARD
// ============================================

async function deleteCard(cardId) {
    if (!confirm('Möchtest du diese Karte wirklich löschen?')) return;

    try {
        const response = await fetch(`/api/cards/${cardId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast('Karte gelöscht', 'success');
            openDeck(currentDeck.id);
        } else {
            showToast(data.error || 'Fehler beim Löschen', 'error');
        }
    } catch (error) {
        console.error('Error deleting card:', error);
        showToast('Fehler beim Löschen', 'error');
    }
}

// ============================================
// DECK SETTINGS
// ============================================

function openDeckSettings(deckId) {
    const deck = currentDeck;

    openSheet(`
        <div class="sheet-header">
            <h3 style="margin:0; font-size:20px; font-weight:700;">Deck-Einstellungen</h3>
            <div class="sheet-close-btn" onclick="closeSheet()">
                <i data-lucide="x"></i>
            </div>
        </div>
        
        <input type="text" id="edit-deck-title" class="ios-input" placeholder="Deck-Titel" value="${escapeHtml(deck.title)}" required>
        <textarea id="edit-deck-description" class="ios-input" placeholder="Beschreibung (optional)" rows="3">${escapeHtml(deck.description || '')}</textarea>
        
        <div style="display:flex; align-items:center; justify-content:space-between; padding:16px; background:var(--tab-bg); border-radius:12px; margin-bottom:15px;">
            <span style="font-weight:600;">Öffentlich teilen</span>
            <div class="ios-toggle ${deck.is_public ? 'active' : ''}" id="edit-deck-public-toggle" onclick="this.classList.toggle('active')">
                <div class="ios-toggle-knob"></div>
            </div>
        </div>
        
        <button class="ios-btn" onclick="updateDeck(${deckId})" style="margin-bottom:10px;">Speichern</button>
        <button class="ios-btn btn-danger-light" onclick="deleteDeck(${deckId})">Deck löschen</button>
    `);

    lucide.createIcons();
}

async function updateDeck(deckId) {
    const title = document.getElementById('edit-deck-title').value.trim();
    const description = document.getElementById('edit-deck-description').value.trim();
    const isPublic = document.getElementById('edit-deck-public-toggle').classList.contains('active');

    if (!title) {
        showToast('Bitte gib einen Titel ein', 'error');
        return;
    }

    try {
        const response = await fetch(`/api/decks/${deckId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, is_public: isPublic })
        });

        const data = await response.json();

        if (data.success) {
            showToast('Deck aktualisiert!', 'success');
            closeSheet();
            openDeck(deckId);
        } else {
            showToast(data.error || 'Fehler beim Aktualisieren', 'error');
        }
    } catch (error) {
        console.error('Error updating deck:', error);
        showToast('Fehler beim Aktualisieren', 'error');
    }
}

async function deleteDeck(deckId) {
    if (!confirm('Möchtest du dieses Deck wirklich löschen? Alle Karten werden ebenfalls gelöscht!')) return;

    try {
        const response = await fetch(`/api/decks/${deckId}/delete`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast('Deck gelöscht', 'success');
            closeSheet();
            navigate('flashcards', null, 'Lernkarten');
        } else {
            showToast(data.error || 'Fehler beim Löschen', 'error');
        }
    } catch (error) {
        console.error('Error deleting deck:', error);
        showToast('Fehler beim Löschen', 'error');
    }
}

// ============================================
// UTILITY
// ============================================

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
