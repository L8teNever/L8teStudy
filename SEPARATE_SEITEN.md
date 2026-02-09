# L8teStudy - Separate HTML-Seiten Struktur

## ✅ Was wurde gemacht?

Die L8teStudy-App wurde von einer Single-Page-Application (SPA) zu einer Multi-Page-Application (MPA) umgebaut. **Jede Hauptseite hat jetzt ihre eigene HTML-Datei!**

## 📁 Neue Struktur

### Templates
```
templates/
├── base.html                   # Basis-Template mit Layout
├── index.html                  # Alte SPA-Version (Backup)
│
├── components/                 # Wiederverwendbare Komponenten
│   ├── header.html
│   ├── side_nav.html
│   ├── bottom_nav.html
│   ├── fab.html
│   └── sheets.html
│
└── pages/                      # ⭐ NEUE SEPARATE SEITEN ⭐
    ├── home.html               # Startseite
    ├── tasks.html              # Aufgaben
    ├── calendar.html           # Kalender
    ├── stundenplan.html        # Stundenplan
    ├── grades.html             # Noten
    ├── flashcards.html         # Lernkarten
    ├── drive.html              # Drive
    ├── mealplan.html           # Essensplan
    └── blackboard.html         # Schwarzes Brett
```

## 🎯 Wie es funktioniert

### 1. Basis-Template (base.html)
Alle Seiten erweitern das Basis-Template:
```html
{% extends "base.html" %}
```

Das Basis-Template enthält:
- Header mit Navigation
- Side Navigation (Desktop)
- Bottom Navigation (Mobile)
- Gemeinsame Styles und Scripts
- Jinja2-Blocks für Anpassungen

### 2. Seiten-Templates (pages/*.html)
Jede Seite überschreibt nur die benötigten Blocks:

```html
{% extends "base.html" %}

{% block title %}Aufgaben - L8teStudy{% endblock %}
{% block current_page %}tasks{% endblock %}
{% block page_title %}Aufgaben{% endblock %}

{% block fab %}
<button class="fab visible" onclick="openCreateTaskSheet()">
    <i data-lucide="plus"></i>
</button>
{% endblock %}

{% block scripts %}
<script>
    // Seiten-spezifisches JavaScript
    await renderTasks();
</script>
{% endblock %}
```

### 3. Flask-Routen
Neue Routen für jede Seite:

```python
@main_bp.route('/<class_name>/home')
def class_home(class_name):
    return render_template('pages/home.html', ...)

@main_bp.route('/<class_name>/tasks')
def class_tasks(class_name):
    return render_template('pages/tasks.html', ...)

@main_bp.route('/<class_name>/calendar')
def class_calendar(class_name):
    return render_template('pages/calendar.html', ...)

# ... und so weiter
```

## 🔄 Unterschied zu vorher

### Vorher (SPA):
```
URL: /KlasseA/tasks
↓
Lädt: index.html
↓
JavaScript rendert: Tasks-Ansicht dynamisch
```

### Jetzt (MPA):
```
URL: /KlasseA/tasks
↓
Lädt: pages/tasks.html (eigene Datei!)
↓
JavaScript initialisiert: Tasks-Funktionen
```

## ⭐ Vorteile

1. **Klarere Struktur**
   - Jede Seite in eigener Datei
   - Einfacher zu finden und bearbeiten
   - Bessere Übersicht

2. **Schnellere Ladezeiten**
   - Nur benötigtes HTML wird geladen
   - Weniger JavaScript-Rendering
   - Bessere Performance

3. **SEO-freundlich**
   - Jede Seite hat eigene URL
   - Eigener Title-Tag
   - Besser für Suchmaschinen

4. **Einfachere Wartung**
   - Seite bearbeiten → nur eine Datei
   - Keine Navigation durch riesige index.html
   - Weniger Fehleranfällig

## 📋 Verfügbare Seiten

| Seite | Template | URL | FAB |
|-------|----------|-----|-----|
| **Home** | `pages/home.html` | `/<klasse>/home` | ❌ |
| **Aufgaben** | `pages/tasks.html` | `/<klasse>/tasks` | ✅ |
| **Kalender** | `pages/calendar.html` | `/<klasse>/calendar` | ✅ |
| **Stundenplan** | `pages/stundenplan.html` | `/<klasse>/stundenplan` | ❌ |
| **Noten** | `pages/grades.html` | `/<klasse>/grades` | ✅ |
| **Lernkarten** | `pages/flashcards.html` | `/<klasse>/flashcards` | ❌ |
| **Drive** | `pages/drive.html` | `/<klasse>/drive` | ❌ |
| **Essensplan** | `pages/mealplan.html` | `/<klasse>/mealplan` | ✅ (Admin) |
| **Infos** | `pages/blackboard.html` | `/<klasse>/blackboard` | ✅ (Admin) |

## 🛠️ Neue Seite hinzufügen

1. **Template erstellen:**
```html
<!-- templates/pages/meine_seite.html -->
{% extends "base.html" %}

{% block title %}Meine Seite - L8teStudy{% endblock %}
{% block current_page %}meine_seite{% endblock %}
{% block page_title %}Meine Seite{% endblock %}

{% block scripts %}
<script>
    document.addEventListener('DOMContentLoaded', async function() {
        lucide.createIcons();
        // Deine Initialisierung
    });
</script>
{% endblock %}
```

2. **Route hinzufügen (routes.py):**
```python
@main_bp.route('/<class_name>/meine-seite')
def class_meine_seite(class_name):
    # ... Permission checks ...
    return render_template('pages/meine_seite.html', 
                         user=current_user, 
                         active_class=target_class,
                         version=get_version())
```

3. **Navigation aktualisieren:**
- Füge Link in `components/side_nav.html` hinzu
- Oder in `components/bottom_nav.html` für Mobile

## 🔧 Integration in routes.py

Die Datei `NEW_ROUTES.py` enthält alle neuen Routen. Diese müssen in `app/routes.py` eingefügt werden:

1. **Öffne** `app/routes.py`
2. **Ersetze** die `class_view` Funktion (Zeile 155-175) mit den neuen Routen aus `NEW_ROUTES.py`
3. **Füge** die `get_version()` Funktion am Ende hinzu
4. **Teste** die App

## ⚠️ Wichtig

### Navigation
Die Navigation funktioniert jetzt mit echten Links statt JavaScript:
```html
<!-- Vorher (SPA) -->
<a onclick="navigate('tasks', this, 'Aufgaben')">

<!-- Jetzt (MPA) -->
<a href="/KlasseA/tasks">
```

### JavaScript
Das JavaScript in `static/js/app.js` bleibt größtenteils gleich, aber:
- `navigate()` Funktion wird weniger gebraucht
- Jede Seite ruft ihre eigene `render*()` Funktion auf
- Keine dynamischen View-Wechsel mehr

### Kompatibilität
Die alte `index.html` (SPA) bleibt als Backup erhalten. Falls Probleme auftreten:
1. Benenne `index.html` um zu `index_new.html`
2. Benenne `index_old.html` um zu `index.html`
3. Entferne die neuen Routen aus `routes.py`

## 📊 Statistiken

| Metrik | SPA (vorher) | MPA (jetzt) |
|--------|--------------|-------------|
| **Haupt-Template** | 1 Datei (9679 Zeilen) | 1 Basis + 9 Seiten |
| **Ladezeit** | Alles auf einmal | Nur benötigte Seite |
| **SEO** | ⭐ | ⭐⭐⭐⭐⭐ |
| **Wartbarkeit** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐ | ⭐⭐⭐⭐ |

## 🚀 Nächste Schritte

1. **Routes integrieren**
   - Kopiere Routen aus `NEW_ROUTES.py` nach `app/routes.py`

2. **Testen**
   - Starte die App
   - Teste alle Seiten
   - Prüfe Navigation

3. **Anpassen**
   - Passe `base.html` nach Bedarf an
   - Füge weitere Seiten hinzu
   - Optimiere Performance

## 💡 Tipps

- **Gemeinsame Elemente** gehören in `base.html`
- **Seiten-spezifisches** gehört in `pages/*.html`
- **Wiederverwendbare Komponenten** gehören in `components/`
- **JavaScript-Funktionen** bleiben in `static/js/app.js`

---

**Status:** ✅ Struktur erstellt, bereit zur Integration
**Datum:** 2026-02-09
**Typ:** Multi-Page-Application (MPA)
