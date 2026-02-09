# L8teStudy Struktur-Umbau Plan

## Ziel
Die monolithische `index.html` (9679 Zeilen) in separate, wartbare Dateien aufteilen, während die Funktionalität vollständig erhalten bleibt.

## Neue Struktur

### templates/
```
templates/
├── base.html                    # Basis-Template mit Header, Navigation, gemeinsamen Styles
├── index.html                   # Haupt-Template (lädt alle Komponenten)
│
├── components/                  # Wiederverwendbare UI-Komponenten
│   ├── header.html
│   ├── navigation.html
│   ├── fab.html
│   ├── sheets.html
│   └── modals.html
│
├── pages/                       # Einzelne Seiten/Views
│   ├── home.html
│   ├── tasks.html
│   ├── calendar.html
│   ├── stundenplan.html
│   ├── grades.html
│   ├── flashcards.html
│   ├── drive.html
│   ├── mealplan.html
│   ├── blackboard.html
│   └── settings.html
│
└── styles/                      # CSS in separate Dateien
    ├── base.css
    ├── components.css
    ├── pages.css
    └── animations.css
```

### static/
```
static/
├── js/
│   ├── app.js                   # Haupt-JavaScript (Navigation, gemeinsame Funktionen)
│   ├── tasks.js                 # Tasks-spezifisches JavaScript
│   ├── calendar.js              # Kalender-spezifisches JavaScript
│   ├── grades.js                # Noten-spezifisches JavaScript
│   ├── stundenplan.js           # Stundenplan-spezifisches JavaScript
│   ├── mealplan.js              # Essensplan-spezifisches JavaScript
│   ├── blackboard.js            # Schwarzes Brett-spezifisches JavaScript
│   ├── settings.js              # Einstellungen-spezifisches JavaScript
│   ├── flashcards.js            # (bereits vorhanden)
│   └── drive.js                 # (bereits vorhanden)
│
└── css/
    ├── base.css
    ├── components.css
    ├── pages.css
    └── animations.css
```

## Implementierungsschritte

1. ✅ Plan erstellen
2. ⏳ CSS extrahieren und in separate Dateien aufteilen
3. ⏳ JavaScript extrahieren und modularisieren
4. ⏳ HTML-Komponenten in separate Dateien aufteilen
5. ⏳ Seiten-spezifische Templates erstellen
6. ⏳ Neues `index.html` mit Includes erstellen
7. ⏳ Testen und Fehler beheben

## Vorteile
- ✅ Bessere Wartbarkeit
- ✅ Einfacheres Debugging
- ✅ Teamarbeit wird einfacher
- ✅ Schnellere Ladezeiten (durch Caching)
- ✅ Gleiche Funktionalität wie vorher
