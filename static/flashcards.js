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
            <div style="margin-bottom: 30px; animation: fadeIn 0.3s ease;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                    <h2 style="margin:0; font-size:24px; font-weight:700;">${(typeof t === 'function' ? t('my_decks') : 'Meine Decks')}</h2>
                    <button class="ios-btn btn-small btn-sec" onclick="openImportDeckSheet()" style="width:auto; padding: 6px 12px; height: 32px; display: inline-flex; align-items: center;">
                        <i data-lucide="upload" style="width:16px; height:16px; margin-right:6px;"></i> Import
                    </button>
                </div>
                
                ${myDecks.length === 0 ? `
                    <div class="floating-card" style="text-align:center; padding:40px 20px;">
                        <i data-lucide="layers" style="width:48px; height:48px; margin-bottom:16px; opacity:0.3;"></i>
                        <p style="margin:0; color:var(--text-sec);">${(typeof t === 'function' ? t('create_first_deck') : 'Erstelle dein erstes Deck!')}</p>
                        <button class="ios-btn btn-small" onclick="openCreateDeckSheet()" style="margin-top:15px; width:auto; display:inline-flex; align-items:center;">
                            <i data-lucide="plus" style="width:16px; height:16px; margin-right:6px;"></i> Neu
                        </button>
                    </div>
                ` : `
                    <div class="deck-grid">
                        ${myDecks.map(deck => `
                            <div class="deck-card" onclick="openDeck(${deck.id})">
                                <div class="deck-title">${escapeHtml(deck.title)}</div>
                                <div class="deck-stats">
                                    ${deck.card_count} ${(deck.card_count === 1 ? 'Karte' : 'Karten')}
                                </div>
                                ${deck.is_public ? '<div class="deck-badge" style="background:rgba(0,0,0,0.05); color:var(--text-sec); top:auto; bottom:15px; right:15px; font-weight:600;">Öffentlich</div>' : ''}
                                ${deck.new_count > 0 ? `<div class="deck-badge" style="background:var(--accent);">${deck.new_count}</div>` : ''}
                            </div>
                        `).join('')}
                         <div class="deck-card add-deck-card" onclick="openCreateDeckSheet()">
                            <div style="display:flex; flex-direction:column; align-items:center; gap:8px;">
                                <i data-lucide="plus" style="width:24px; height:24px;"></i>
                                <span style="font-size:13px; font-weight:600;">Neues Deck</span>
                            </div>
                        </div>
                    </div>
                `}
            </div>

            ${publicDecks.length > 0 ? `
                <div style="margin-bottom: 30px; animation: fadeIn 0.4s ease;">
                    <h2 style="margin:0 0 15px 0; font-size:24px; font-weight:700;">${(typeof t === 'function' ? t('public_decks') : 'Öffentliche Decks')}</h2>
                    <div class="deck-grid">
                        ${publicDecks.map(deck => `
                            <div class="deck-card" onclick="openDeck(${deck.id})">
                                <div class="deck-title">${escapeHtml(deck.title)}</div>
                                <div class="deck-stats">
                                    ${deck.card_count} Karten • ${escapeHtml(deck.author_name)}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        `;

        document.getElementById('app-container').innerHTML = html;
        lucide.createIcons();

    } catch (error) {
        console.error('Error loading decks:', error);
        if (typeof showToast === 'function') showToast('Fehler beim Laden der Decks', 'error');
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

        // Update view state
        if (typeof previousView !== 'undefined' && typeof currentView !== 'undefined') {
            previousView = currentView;
            currentView = 'deck-detail';
        }
        if (typeof setPageTitle === 'function') {
            setPageTitle(deck.title);
        }

        const isOwner = deck.is_own;

        let html = `
            <div class="floating-card deck-detail-container" style="position: relative;">
                <div style="margin-bottom: 20px;">
                    <button onclick="renderFlashcardsView()" style="background:none; border:none; padding:0; color:var(--accent); font-weight:600; display:flex; align-items:center; cursor:pointer; font-size:15px; margin-bottom:10px;">
                        <i data-lucide="chevron-left" style="width:20px; height:20px; margin-right:4px;"></i> Zurück
                    </button>
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <h2 style="margin:0 0 8px 0; font-size:28px; font-weight:700;">${escapeHtml(deck.title)}</h2>
                            ${deck.description ? `<p style="margin:0; color:var(--text-sec); font-size:15px;">${escapeHtml(deck.description)}</p>` : ''}
                        </div>
                        ${isOwner ? `
                            <button class="ios-btn btn-small btn-sec" onclick="openDeckSettings(${deckId})" style="min-width:auto; padding:8px 12px; margin-left:10px;">
                                <i data-lucide="settings" style="width:18px; height:18px;"></i>
                            </button>
                        ` : ''}
                    </div>
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
                
                <!--Study Buttons-->
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
                    <button class="ios-btn btn-sec" onclick="openAddCardSheet(${deckId})" style="width:100%; margin-bottom:24px;">
                        <i data-lucide="plus" style="width:18px; height:18px; margin-right:8px;"></i>
                        Karte hinzufügen
                    </button>
                ` : ''
            }

                <!--Card List-->
        ${currentCards.length > 0 ? `
                    <div style="border-top: 1px solid var(--border); padding-top: 20px; margin-top: 20px;">
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
                ` : ''
            }
            </div>
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

    // Update view state
    if (typeof previousView !== 'undefined' && typeof currentView !== 'undefined') {
        previousView = 'deck-detail';
        currentView = 'study';
    }
    if (typeof setPageTitle === 'function') {
        setPageTitle(`${currentDeck.title} - Lernen`);
    }

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
        <div class="floating-card study-mode-container" style="position: relative;">
            <!--Header with Close Button-->
            <div style="position: absolute; top: 15px; right: 15px; z-index: 10;">
                <button onclick="quitStudySession()" style="background: rgba(0,0,0,0.05); border: none; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: var(--text-sec);">
                    <i data-lucide="x" style="width: 20px; height: 20px;"></i>
                </button>
            </div>

            <!--Progress -->
            <div style="margin-bottom:24px; margin-top: 10px;">
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
            
            <!--Card -->
        <div class="flashcard-container" onclick="handleCardClick()" style="cursor:pointer;">
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
            ` : (window.innerWidth < 1024) ? `
                <div style="text-align:center; margin-top:24px; color:var(--text-sec); font-size:13px;">
                    <i data-lucide="swipe" style="width:16px; height:16px; vertical-align:middle; margin-right:4px;"></i>
                    ${studyMode === 'spaced'
                ? 'Wische: ← Schwer | → Gut | ↓ Nochmal'
                : 'Wische nach rechts für nächste Karte'}
                </div>
            ` : ''
        }
        </div>
        `;

    document.getElementById('app-container').innerHTML = html;
    lucide.createIcons();

    // Initialize swipe gestures on mobile/tablet
    if (window.innerWidth < 1024) {
        initCardSwipe();
    }
}

function handleCardClick() {
    // Don't flip if we just finished a swipe
    if (isSwiping) return;
    flipCard();
}

function flipCard() {
    isCardFlipped = !isCardFlipped;
    const cardEl = document.getElementById('study-card');
    if (cardEl) {
        cardEl.classList.toggle('flipped');
    }
}

// ============================================
// SWIPE GESTURES FOR CARDS
// ============================================

let touchStartX = 0;
let touchStartY = 0;
let touchCurrentX = 0;
let touchCurrentY = 0;
let isSwiping = false;

function initCardSwipe() {
    const cardContainer = document.querySelector('.flashcard-container');
    if (!cardContainer) return;

    cardContainer.addEventListener('touchstart', handleTouchStart, { passive: true });
    cardContainer.addEventListener('touchmove', handleTouchMove, { passive: false });
    cardContainer.addEventListener('touchend', handleTouchEnd, { passive: true });
}

function handleTouchStart(e) {
    if (!isCardFlipped) return; // Only allow swipe on flipped cards

    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
    isSwiping = true;
}

function handleTouchMove(e) {
    if (!isSwiping || !isCardFlipped) return;

    touchCurrentX = e.touches[0].clientX;
    touchCurrentY = e.touches[0].clientY;

    const deltaX = touchCurrentX - touchStartX;
    const deltaY = touchCurrentY - touchStartY;

    // Prevent default scrolling when swiping horizontally or down
    if (Math.abs(deltaX) > 10 || deltaY > 10) {
        e.preventDefault();
    }

    const card = document.getElementById('study-card');
    if (!card) return;

    // Apply transform to card
    card.style.transform = `translate(${deltaX}px, ${deltaY}px) rotateZ(${deltaX * 0.1}deg)`;
    card.style.transition = 'none';

    // Show color overlay based on swipe direction
    let overlay = card.querySelector('.swipe-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'swipe-overlay';
        card.appendChild(overlay);
    }

    // Determine swipe direction and color
    const absX = Math.abs(deltaX);
    const absY = Math.abs(deltaY);

    if (absY > absX && deltaY > 50) {
        // Swipe down
        if (deltaX < -30) {
            // Down-left = Again (1)
            overlay.style.background = 'rgba(255, 59, 48, 0.3)';
            overlay.style.opacity = Math.min(deltaY / 150, 0.5);
        } else if (deltaX > 30) {
            // Down-right = Easy (4)
            overlay.style.background = 'rgba(10, 132, 255, 0.3)';
            overlay.style.opacity = Math.min(deltaY / 150, 0.5);
        } else {
            // Straight down = Again (1) by default
            overlay.style.background = 'rgba(255, 59, 48, 0.3)';
            overlay.style.opacity = Math.min(deltaY / 150, 0.5);
        }
    } else if (absX > absY) {
        // Horizontal swipe
        if (deltaX < -50) {
            // Swipe left = Hard (2)
            overlay.style.background = 'rgba(255, 159, 10, 0.3)';
            overlay.style.opacity = Math.min(absX / 150, 0.5);
        } else if (deltaX > 50) {
            // Swipe right = Good (3)
            overlay.style.background = 'rgba(48, 209, 88, 0.3)';
            overlay.style.opacity = Math.min(absX / 150, 0.5);
        }
    } else {
        overlay.style.opacity = 0;
    }
}

function handleTouchEnd(e) {
    if (!isSwiping || !isCardFlipped) return;

    const deltaX = touchCurrentX - touchStartX;
    const deltaY = touchCurrentY - touchStartY;
    const absX = Math.abs(deltaX);
    const absY = Math.abs(deltaY);

    const card = document.getElementById('study-card');
    if (!card) return;

    // Determine if swipe was strong enough
    const swipeThreshold = 80;
    let rating = null;

    if (absY > absX && deltaY > swipeThreshold) {
        // Swipe down
        if (deltaX < -30) {
            rating = 1; // Down-left = Again
        } else if (deltaX > 30) {
            rating = 4; // Down-right = Easy
        } else {
            rating = 1; // Straight down = Again
        }
    } else if (absX > swipeThreshold && absX > absY) {
        // Horizontal swipe
        if (deltaX < 0) {
            rating = 2; // Left = Hard
        } else {
            rating = 3; // Right = Good
        }
    }

    if (rating !== null && studyMode === 'spaced') {
        // Animate card out
        const direction = absX > absY ? (deltaX > 0 ? 'right' : 'left') : 'down';
        animateCardOut(card, direction, () => {
            rateCard(rating);
        });
    } else if (rating !== null && studyMode === 'free') {
        // In free mode, any swipe goes to next card
        animateCardOut(card, 'right', () => {
            nextFreePracticeCard();
        });
    } else {
        // Reset card position
        card.style.transform = '';
        card.style.transition = 'transform 0.3s ease';

        const overlay = card.querySelector('.swipe-overlay');
        if (overlay) {
            overlay.style.opacity = 0;
        }
    }

    isSwiping = false;
    touchStartX = 0;
    touchStartY = 0;
    touchCurrentX = 0;
    touchCurrentY = 0;
}

function animateCardOut(card, direction, callback) {
    const distance = window.innerWidth;
    let transform = '';

    switch (direction) {
        case 'left':
            transform = `translateX(-${distance}px) rotateZ(-30deg)`;
            break;
        case 'right':
            transform = `translateX(${distance}px) rotateZ(30deg)`;
            break;
        case 'down':
            transform = `translateY(${distance}px) rotateZ(10deg)`;
            break;
    }

    card.style.transform = transform;
    card.style.transition = 'transform 0.4s cubic-bezier(0.4, 0.0, 0.2, 1)';
    card.style.opacity = '0';

    setTimeout(() => {
        callback();
    }, 400);
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
    quitStudySession();
}

function quitStudySession() {
    // Reset UI
    document.querySelector('.bottom-nav').style.display = '';
    document.querySelector('.side-nav').style.display = '';
    document.getElementById('study-nav').style.display = 'none';
    document.getElementById('practice-nav').style.display = 'none';

    // Always remove from document flow if possible, though currently just hidding
    // Restore sidebar if on desktop
    if (window.innerWidth >= 768) {
        document.querySelector('.side-nav').style.display = 'flex';
    }

    // Return to deck
    if (currentDeck) {
        openDeck(currentDeck.id);
    } else {
        renderFlashcardsView();
    }
}

// ============================================
// CARD PREVIEW
// ============================================

function previewCard(index) {
    const card = currentCards[index];
    alert(`Vorderseite:\n${card.front}\n\nRückseite:\n${card.back}`);
}

// ============================================
// CREATE/EDIT DECK
// ============================================

function openCreateDeckSheet() {
    const sheetContent = `
        <div class="sheet-header">
            <h3 style="margin:0; font-size:20px; font-weight:700;">Neues Deck erstellen</h3>
            <div class="sheet-close-btn" onclick="closeSheet()">
                <i data-lucide="x" style="width:20px; height:20px;"></i>
            </div>
        </div>
        
        <div style="margin-top: 20px;">
            <input type="text" class="ios-input" id="new-deck-title" placeholder="Deck-Titel" autofocus>
            <textarea class="ios-input" id="new-deck-description" placeholder="Beschreibung (optional)" rows="3"></textarea>
            
            <!-- Visibility Toggle -->
            <div class="account-item" onclick="toggleCreateDeckVisibility()" style="margin-bottom: 20px; border-bottom: none; padding: 16px 0;">
                <div class="account-item-icon">
                    <i data-lucide="eye-off" id="create-visibility-icon" style="width:20px; height:20px;"></i>
                </div>
                <div class="account-item-text" id="create-visibility-text">Privat</div>
                <div class="ios-toggle" id="create-visibility-toggle">
                    <div class="ios-toggle-knob"></div>
                </div>
            </div>
            
            <div class="button-group" style="margin-top: 20px;">
                <button class="ios-btn btn-sec btn-small" onclick="closeSheet()">Abbrechen</button>
                <button class="ios-btn btn-small" onclick="submitCreateDeck()">Erstellen</button>
            </div>
        </div>
    `;

    openSheet(sheetContent);
    setTimeout(() => document.getElementById('new-deck-title')?.focus(), 100);
}

let createDeckIsPublic = false;

function toggleCreateDeckVisibility() {
    createDeckIsPublic = !createDeckIsPublic;
    const toggle = document.getElementById('create-visibility-toggle');
    const icon = document.getElementById('create-visibility-icon');
    const text = document.getElementById('create-visibility-text');

    if (createDeckIsPublic) {
        toggle.classList.add('active');
        icon.setAttribute('data-lucide', 'eye');
        text.textContent = 'Öffentlich';
    } else {
        toggle.classList.remove('active');
        icon.setAttribute('data-lucide', 'eye-off');
        text.textContent = 'Privat';
    }
    lucide.createIcons();
}

function submitCreateDeck() {
    const title = document.getElementById('new-deck-title')?.value.trim();
    const description = document.getElementById('new-deck-description')?.value.trim();

    if (!title) {
        showToast('Bitte gib einen Titel ein', 'error');
        return;
    }

    createDeck(title, description, createDeckIsPublic);
    closeSheet();
    createDeckIsPublic = false; // Reset for next time
}

async function createDeck(title, description, isPublic) {
    try {
        const response = await fetch('/api/decks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, is_public: isPublic })
        });

        const data = await response.json();

        if (response.ok && data.id) {
            if (typeof showToast === 'function') {
                showToast('Deck erstellt!', 'success');
            } else {
                alert('Deck erstellt!');
            }
            // Reload deck list and open new deck
            await renderFlashcardsView();
            setTimeout(() => openDeck(data.id), 100);
        } else {
            if (typeof showToast === 'function') {
                showToast(data.error || 'Fehler beim Erstellen', 'error');
            } else {
                alert(data.error || 'Fehler beim Erstellen');
            }
        }
    } catch (error) {
        console.error('Error creating deck:', error);
        if (typeof showToast === 'function') {
            showToast('Fehler beim Erstellen', 'error');
        } else {
            alert('Fehler beim Erstellen');
        }
    }
}

// ============================================
// ADD CARD
// ============================================

function openAddCardSheet(deckId) {
    const sheetContent = `
        <div class="sheet-header">
            <h3 style="margin:0; font-size:20px; font-weight:700;">Neue Karte hinzufügen</h3>
            <div class="sheet-close-btn" onclick="closeSheet()">
                <i data-lucide="x" style="width:20px; height:20px;"></i>
            </div>
        </div>
        
        <div style="margin-top: 20px;">
            <label style="display: block; font-size: 13px; font-weight: 600; color: var(--text-sec); margin-bottom: 8px;">Vorderseite (Frage)</label>
            <textarea class="ios-input" id="card-front" placeholder="Was möchtest du lernen?" rows="3" autofocus></textarea>
            
            <label style="display: block; font-size: 13px; font-weight: 600; color: var(--text-sec); margin-bottom: 8px; margin-top: 15px;">Rückseite (Antwort)</label>
            <textarea class="ios-input" id="card-back" placeholder="Die Antwort..." rows="3"></textarea>
            
            <div class="button-group" style="margin-top: 20px;">
                <button class="ios-btn btn-sec btn-small" onclick="closeSheet()">Abbrechen</button>
                <button class="ios-btn btn-small" onclick="submitAddCard(${deckId})">Hinzufügen</button>
            </div>
        </div>
    `;

    openSheet(sheetContent);
    setTimeout(() => document.getElementById('card-front')?.focus(), 100);
}

function submitAddCard(deckId) {
    const front = document.getElementById('card-front')?.value.trim();
    const back = document.getElementById('card-back')?.value.trim();

    if (!front) {
        showToast('Bitte gib eine Frage ein', 'error');
        return;
    }

    if (!back) {
        showToast('Bitte gib eine Antwort ein', 'error');
        return;
    }

    addCard(deckId, front, back);
    closeSheet();
}

async function addCard(deckId, front, back) {
    try {
        const response = await fetch(`/api/decks/${deckId}/cards`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ front, back })
        });

        const data = await response.json();

        if (data.success || response.ok) {
            if (typeof showToast === 'function') {
                showToast('Karte hinzugefügt!', 'success');
            } else {
                alert('Karte hinzugefügt!');
            }
            openDeck(deckId);
        } else {
            if (typeof showToast === 'function') {
                showToast(data.error || 'Fehler beim Hinzufügen', 'error');
            } else {
                alert(data.error || 'Fehler beim Hinzufügen');
            }
        }
    } catch (error) {
        console.error('Error adding card:', error);
        if (typeof showToast === 'function') {
            showToast('Fehler beim Hinzufügen', 'error');
        } else {
            alert('Fehler beim Hinzufügen');
        }
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
    // Initialize toggle state
    window.editDeckIsPublic = deck.is_public;

    const sheetContent = `
        <div class="sheet-header">
            <h3 style="margin:0; font-size:20px; font-weight:700;">Deck bearbeiten</h3>
            <div class="sheet-close-btn" onclick="closeSheet()">
                <i data-lucide="x" style="width:20px; height:20px;"></i>
            </div>
        </div>
        
        <div style="margin-top: 20px;">
            <!-- Title Input -->
            <label style="display: block; font-size: 13px; font-weight: 600; color: var(--text-sec); margin-bottom: 8px;">
                <i data-lucide="edit-3" style="width:14px; height:14px; vertical-align: middle; margin-right: 4px;"></i>
                Titel
            </label>
            <input type="text" class="ios-input" id="edit-deck-title" placeholder="Deck-Titel" value="${escapeHtml(deck.title)}" autofocus>
            
            <!-- Description Input -->
            <label style="display: block; font-size: 13px; font-weight: 600; color: var(--text-sec); margin-bottom: 8px; margin-top: 15px;">
                <i data-lucide="file-text" style="width:14px; height:14px; vertical-align: middle; margin-right: 4px;"></i>
                Beschreibung
            </label>
            <textarea class="ios-input" id="edit-deck-description" placeholder="Beschreibung (optional)" rows="3">${escapeHtml(deck.description || '')}</textarea>
            
            <!-- Visibility Toggle -->
            <label style="display: block; font-size: 13px; font-weight: 600; color: var(--text-sec); margin-bottom: 8px; margin-top: 15px;">
                <i data-lucide="eye" style="width:14px; height:14px; vertical-align: middle; margin-right: 4px;"></i>
                Sichtbarkeit
            </label>
            <div class="account-item" onclick="toggleEditDeckVisibility()" style="margin-bottom: 20px; border-bottom: none; padding: 16px; background: var(--tab-bg); border-radius: 12px;">
                <div class="account-item-icon">
                    <i data-lucide="${deck.is_public ? 'eye' : 'eye-off'}" id="edit-visibility-icon" style="width:20px; height:20px;"></i>
                </div>
                <div class="account-item-text" id="edit-visibility-text">
                    ${deck.is_public ? 'Öffentlich' : 'Privat'}
                </div>
                <div class="ios-toggle ${deck.is_public ? 'active' : ''}" id="edit-visibility-toggle">
                    <div class="ios-toggle-knob"></div>
                </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="button-group" style="margin-top: 20px; flex-direction: column; gap: 10px;">
                <button class="ios-btn" onclick="submitDeckEdit(${deckId})">
                    <i data-lucide="save" style="width:18px; height:18px; margin-right:8px;"></i>
                    Änderungen speichern
                </button>
                <button class="ios-btn" style="background: var(--danger);" onclick="confirmDeleteDeckInline(${deckId})">
                    <i data-lucide="trash-2" style="width:18px; height:18px; margin-right:8px;"></i>
                    Deck löschen
                </button>
                <button class="ios-btn btn-sec" onclick="closeSheet()">Abbrechen</button>
            </div>
        </div>
    `;

    openSheet(sheetContent);
    setTimeout(() => document.getElementById('edit-deck-title')?.focus(), 100);
}

function toggleEditDeckVisibility() {
    window.editDeckIsPublic = !window.editDeckIsPublic;
    const toggle = document.getElementById('edit-visibility-toggle');
    const icon = document.getElementById('edit-visibility-icon');
    const text = document.getElementById('edit-visibility-text');

    if (window.editDeckIsPublic) {
        toggle.classList.add('active');
        icon.setAttribute('data-lucide', 'eye');
        text.textContent = 'Öffentlich';
    } else {
        toggle.classList.remove('active');
        icon.setAttribute('data-lucide', 'eye-off');
        text.textContent = 'Privat';
    }
    lucide.createIcons();
}

function submitDeckEdit(deckId) {
    const newTitle = document.getElementById('edit-deck-title')?.value.trim();
    const newDescription = document.getElementById('edit-deck-description')?.value.trim();

    if (!newTitle) {
        showToast('Bitte gib einen Titel ein', 'error');
        return;
    }

    updateDeck(deckId, newTitle, newDescription, window.editDeckIsPublic);
    closeSheet();
}

function confirmDeleteDeckInline(deckId) {
    const sheetContent = `
        <div class="sheet-header">
            <h3 style="margin:0; font-size:20px; font-weight:700; color: var(--danger);">
                <i data-lucide="alert-triangle" style="width:22px; height:22px; vertical-align: middle; margin-right: 8px;"></i>
                Deck löschen?
            </h3>
            <div class="sheet-close-btn" onclick="openDeckSettings(${deckId})">
                <i data-lucide="x" style="width:20px; height:20px;"></i>
            </div>
        </div>
        
        <div style="margin-top: 20px;">
            <div style="background: rgba(255, 59, 48, 0.1); padding: 16px; border-radius: 12px; margin-bottom: 20px;">
                <p style="color: var(--danger); margin: 0; line-height: 1.5; font-weight: 600;">
                    ⚠️ Achtung: Diese Aktion kann nicht rückgängig gemacht werden!
                </p>
            </div>
            
            <p style="color: var(--text-sec); margin: 0 0 20px 0; line-height: 1.5;">
                Möchtest du das Deck <strong>"${escapeHtml(currentDeck.title)}"</strong> wirklich löschen? 
                Alle <strong>${currentDeck.cards?.length || 0} Karten</strong> werden ebenfalls gelöscht.
            </p>
            
            <div class="button-group" style="margin-top: 20px; flex-direction: column; gap: 10px;">
                <button class="ios-btn" style="background: var(--danger);" onclick="deleteDeck(${deckId})">
                    <i data-lucide="trash-2" style="width:18px; height:18px; margin-right:8px;"></i>
                    Ja, Deck löschen
                </button>
                <button class="ios-btn btn-sec" onclick="openDeckSettings(${deckId})">
                    <i data-lucide="arrow-left" style="width:18px; height:18px; margin-right:8px;"></i>
                    Zurück zu Einstellungen
                </button>
            </div>
        </div>
    `;

    openSheet(sheetContent);
}

async function updateDeck(deckId, title, description, isPublic) {
    try {
        const response = await fetch(`/api/decks/${deckId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, is_public: isPublic })
        });

        const data = await response.json();

        if (data.success || response.ok) {
            if (typeof showToast === 'function') {
                showToast('Deck aktualisiert!', 'success');
            } else {
                alert('Deck aktualisiert!');
            }
            openDeck(deckId);
        } else {
            if (typeof showToast === 'function') {
                showToast(data.error || 'Fehler beim Aktualisieren', 'error');
            } else {
                alert(data.error || 'Fehler beim Aktualisieren');
            }
        }
    } catch (error) {
        console.error('Error updating deck:', error);
        if (typeof showToast === 'function') {
            showToast('Fehler beim Aktualisieren', 'error');
        } else {
            alert('Fehler beim Aktualisieren');
        }
    }
}

async function deleteDeck(deckId) {
    closeSheet(); // Close the confirmation sheet

    try {
        const response = await fetch(`/api/decks/${deckId}/delete`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success || response.ok) {
            if (typeof showToast === 'function') {
                showToast('Deck gelöscht', 'success');
            } else {
                alert('Deck gelöscht');
            }
            // Navigate back to flashcards list
            if (typeof navigate === 'function') {
                navigate('flashcards', null, 'Lernkarten');
            } else {
                renderFlashcardsView();
            }
        } else {
            if (typeof showToast === 'function') {
                showToast(data.error || 'Fehler beim Löschen', 'error');
            } else {
                alert(data.error || 'Fehler beim Löschen');
            }
        }
    } catch (error) {
        console.error('Error deleting deck:', error);
        if (typeof showToast === 'function') {
            showToast('Fehler beim Löschen', 'error');
        } else {
            alert('Fehler beim Löschen');
        }
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

// ============================================
// IMPORT DECK
// ============================================

function openImportDeckSheet() {
    let input = document.getElementById('deck-import-input');
    if (!input) {
        input = document.createElement('input');
        input.type = 'file';
        input.id = 'deck-import-input';
        input.accept = '.csv,.txt,.apkg';
        input.style.display = 'none';
        input.onchange = (e) => {
            if (e.target.files.length > 0) {
                uploadDeckFile(e.target.files[0]);
            }
            e.target.value = '';
        };
        document.body.appendChild(input);
    }
    input.click();
}

async function uploadDeckFile(file) {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    // Initial user feedback
    if (typeof showToast === 'function') showToast('Importiere Deck...', 'info');

    try {
        const response = await fetch('/api/decks/import', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            if (typeof showToast === 'function') {
                showToast(`Deck importiert! (${data.count} Karten)`, 'success');
            } else {
                alert(`Deck importiert! (${data.count} Karten)`);
            }
            await renderFlashcardsView();
        } else {
            if (typeof showToast === 'function') {
                showToast(data.error || 'Fehler beim Import', 'error');
            } else {
                alert(data.error || 'Fehler beim Import');
            }
        }
    } catch (error) {
        console.error('Import Error:', error);
        if (typeof showToast === 'function') {
            showToast('Verbindungsfehler beim Import', 'error');
        } else {
            alert('Verbindungsfehler beim Import');
        }
    }
}
