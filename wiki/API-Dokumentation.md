# API-Dokumentation

Vollständige Dokumentation aller API-Endpunkte von L8teStudy.

---

## 🔐 Authentifizierung

Alle API-Endpunkte (außer Login) erfordern eine aktive Session. Die Authentifizierung erfolgt über Session-Cookies.

### Login

**POST** `/auth/login`

Benutzer anmelden und Session erstellen.

**Request Body** (Form Data):
```
class_code: string (Klassencode)
username: string
password: string
```

**Response** (200 OK):
```json
{
  "success": true,
  "redirect": "/",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "super_admin",
    "class_id": null
  }
}
```

**Response** (401 Unauthorized):
```json
{
  "success": false,
  "message": "Ungültige Zugangsdaten"
}
```

### Logout

**GET** `/auth/logout`

Benutzer abmelden und Session beenden.

**Response**: Redirect zu `/login`

---

## 📚 Aufgaben (Tasks)

### Alle Aufgaben abrufen

**GET** `/api/tasks`

**Query Parameters**:
- `filter`: `open` | `completed` | `all` (default: `all`)

**Response** (200 OK):
```json
{
  "success": true,
  "tasks": [
    {
      "id": 1,
      "title": "Mathe Hausaufgabe",
      "description": "Seite 42, Aufgaben 1-5",
      "subject": "Mathematik",
      "subject_id": 3,
      "due_date": "2026-01-15T00:00:00",
      "is_done": false,
      "is_shared": false,
      "author": {
        "id": 2,
        "username": "lehrer1"
      },
      "images": [
        {
          "id": 1,
          "filename": "aufgabe.jpg",
          "url": "/uploads/aufgabe.jpg"
        }
      ],
      "unread_count": 3
    }
  ]
}
```

### Aufgabe erstellen

**POST** `/api/tasks`

**Request Body** (Form Data):
```
title: string (erforderlich)
description: string
subject: string (Legacy, optional)
subject_id: integer (optional)
due_date: string (YYYY-MM-DD)
is_shared: boolean (default: false)
class_id: integer (optional)
images: file[] (optional, mehrere Dateien)
```

**Response** (201 Created):
```json
{
  "success": true,
  "task": {
    "id": 5,
    "title": "Neue Aufgabe",
    ...
  }
}
```

### Aufgabe bearbeiten

**PUT** `/api/tasks/<id>`

**Request Body**: Wie bei POST, alle Felder optional

**Response** (200 OK):
```json
{
  "success": true,
  "task": { ... }
}
```

### Aufgabe löschen

**DELETE** `/api/tasks/<id>`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Aufgabe gelöscht"
}
```

### Aufgabe als erledigt/offen markieren

**POST** `/api/tasks/<id>/toggle`

**Response** (200 OK):
```json
{
  "success": true,
  "is_done": true
}
```

---

## 📅 Termine (Events)

### Alle Termine abrufen

**GET** `/api/events`

**Query Parameters**:
- `start`: string (YYYY-MM-DD, optional)
- `end`: string (YYYY-MM-DD, optional)

**Response** (200 OK):
```json
{
  "success": true,
  "events": [
    {
      "id": 1,
      "title": "Mathe Klausur",
      "description": "Kapitel 1-3",
      "date": "2026-01-20T10:00:00",
      "subject": "Mathematik",
      "subject_id": 3,
      "is_shared": false,
      "author": {
        "id": 2,
        "username": "lehrer1"
      }
    }
  ]
}
```

### Termin erstellen

**POST** `/api/events`

**Request Body** (JSON):
```json
{
  "title": "Neue Klausur",
  "description": "Wichtig!",
  "date": "2026-01-25",
  "time": "10:00",
  "subject_id": 3,
  "is_shared": false
}
```

### Termin bearbeiten

**PUT** `/api/events/<id>`

### Termin löschen

**DELETE** `/api/events/<id>`

---

## 📊 Noten (Grades)

### Alle Noten abrufen

**GET** `/api/grades`

**Response** (200 OK):
```json
{
  "success": true,
  "grades": [
    {
      "id": 1,
      "subject": "Mathematik",
      "value": 2.0,
      "weight": 1.0,
      "title": "Klausur 1",
      "date": "2026-01-10T00:00:00",
      "description": "Gut gemacht!"
    }
  ],
  "averages": {
    "Mathematik": 2.3,
    "Deutsch": 1.8,
    "total": 2.05
  }
}
```

### Note erstellen

**POST** `/api/grades`

**Request Body** (JSON):
```json
{
  "subject": "Mathematik",
  "value": 2.0,
  "weight": 1.0,
  "title": "Klausur 1",
  "description": "Optional"
}
```

### Note bearbeiten

**PUT** `/api/grades/<id>`

### Note löschen

**DELETE** `/api/grades/<id>`

---

## 📖 Fächer (Subjects)

### Alle Fächer abrufen

**GET** `/api/subjects`

**Response** (200 OK):
```json
{
  "success": true,
  "subjects": [
    {
      "id": 1,
      "name": "Mathematik",
      "classes": [
        {"id": 1, "name": "10a"}
      ]
    }
  ]
}
```

### Fach erstellen

**POST** `/api/subjects`

**Request Body** (JSON):
```json
{
  "name": "Informatik",
  "class_id": 1
}
```

### Fach löschen

**DELETE** `/api/subjects/<id>`

### Fächer von WebUntis importieren

**POST** `/api/subjects/import-untis`

**Response** (200 OK):
```json
{
  "success": true,
  "imported": 12,
  "subjects": [...]
}
```

---

## 💬 Chat

### Chat-Nachrichten abrufen

**GET** `/api/tasks/<task_id>/messages`

**Response** (200 OK):
```json
{
  "success": true,
  "messages": [
    {
      "id": 1,
      "content": "Hallo!",
      "message_type": "text",
      "user": {
        "id": 2,
        "username": "user1"
      },
      "created_at": "2026-01-12T10:30:00",
      "parent_id": null,
      "replies": []
    }
  ]
}
```

### Nachricht senden

**POST** `/api/tasks/<task_id>/messages`

**Request Body** (Form Data):
```
content: string (für Text-Nachrichten)
file: file (für Bild/Datei-Nachrichten)
parent_id: integer (optional, für Antworten)
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": { ... }
}
```

### Chat als gelesen markieren

**POST** `/api/tasks/<task_id>/mark-read`

### Ungelesene Nachrichten zählen

**GET** `/api/tasks/unread-counts`

**Response** (200 OK):
```json
{
  "success": true,
  "counts": {
    "1": 3,
    "5": 1
  }
}
```

---

## 🕐 WebUntis

### Stundenplan abrufen

**GET** `/api/untis/timetable`

**Query Parameters**:
- `date`: string (YYYY-MM-DD, optional, default: heute)

**Response** (200 OK):
```json
{
  "success": true,
  "timetable": [
    {
      "date": "2026-01-13",
      "startTime": "08:00",
      "endTime": "08:45",
      "subject": "Mathematik",
      "teacher": "Müller",
      "room": "R101",
      "code": "cancelled|substitution|normal"
    }
  ]
}
```

### Zugangsdaten speichern

**POST** `/api/untis/credentials`

**Request Body** (JSON):
```json
{
  "server": "mese.webuntis.com",
  "school": "gymnasium-beispiel",
  "username": "schueler1",
  "password": "passwort",
  "untis_class_name": "10a"
}
```

### Zugangsdaten abrufen

**GET** `/api/untis/credentials`

---

## 👥 Benutzerverwaltung (Admin)

### Benutzer abrufen

**GET** `/api/users`

**Berechtigung**: Admin oder Super Admin

**Response** (200 OK):
```json
{
  "success": true,
  "users": [
    {
      "id": 1,
      "username": "user1",
      "role": "student",
      "class_id": 1,
      "created_at": "2026-01-01T00:00:00"
    }
  ]
}
```

### Benutzer erstellen

**POST** `/api/users`

**Berechtigung**: Admin oder Super Admin

**Request Body** (JSON):
```json
{
  "username": "newuser",
  "password": "SecurePass123",
  "role": "student",
  "class_id": 1
}
```

### Benutzer löschen

**DELETE** `/api/users/<id>`

**Berechtigung**: Admin oder Super Admin

---

## 🏫 Klassenverwaltung (Super Admin)

### Klassen abrufen

**GET** `/api/classes`

**Berechtigung**: Super Admin

### Klasse erstellen

**POST** `/api/classes`

**Berechtigung**: Super Admin

**Request Body** (JSON):
```json
{
  "name": "10b",
  "code": "CLASS2"
}
```

### Klasse bearbeiten

**PUT** `/api/classes/<id>`

**Berechtigung**: Admin (eigene Klasse) oder Super Admin

### Klasse löschen

**DELETE** `/api/classes/<id>`

**Berechtigung**: Super Admin

---

## 🔔 Benachrichtigungen

### Einstellungen abrufen

**GET** `/api/notification-settings`

### Einstellungen speichern

**POST** `/api/notification-settings`

**Request Body** (JSON):
```json
{
  "notify_new_task": true,
  "notify_new_event": true,
  "notify_chat_message": true,
  "reminder_homework": "17:00",
  "reminder_exam": "19:00"
}
```

### Push abonnieren

**POST** `/api/push/subscribe`

**Request Body** (JSON):
```json
{
  "endpoint": "https://...",
  "keys": {
    "auth": "...",
    "p256dh": "..."
  }
}
```

### Push abbestellen

**POST** `/api/push/unsubscribe`

### Test-Benachrichtigung senden

**POST** `/api/push/test`

---

## 💾 Backup & Restore (Super Admin)

### Datenbank exportieren

**GET** `/api/backup/export`

**Berechtigung**: Super Admin

**Response**: JSON-Datei (Download)

### Datenbank importieren

**POST** `/api/backup/import`

**Berechtigung**: Super Admin

**Request Body** (Form Data):
```
file: file (JSON-Backup-Datei)
```

---

## 🔒 Sicherheit

### CSRF-Schutz

Alle POST/PUT/DELETE-Requests außer `/api/*` benötigen ein CSRF-Token.

**Token abrufen**: Automatisch in Forms via Flask-WTF

### Rate Limiting

- **Login**: 5 Versuche pro Minute
- **API**: 100 Requests pro Minute
- **Upload**: 10 Uploads pro Minute

### Fehler-Responses

**400 Bad Request**:
```json
{
  "success": false,
  "message": "Ungültige Anfrage"
}
```

**401 Unauthorized**:
```json
{
  "success": false,
  "message": "Nicht angemeldet"
}
```

**403 Forbidden**:
```json
{
  "success": false,
  "message": "Keine Berechtigung"
}
```

**404 Not Found**:
```json
{
  "success": false,
  "message": "Nicht gefunden"
}
```

**500 Internal Server Error**:
```json
{
  "success": false,
  "message": "Serverfehler"
}
```

---

## 📚 Weitere Ressourcen

- **[Architektur](Architektur)** - Projektstruktur
- **[Datenbank-Schema](Datenbank-Schema)** - Modelle
- **[Entwicklung](Entwicklung)** - Entwicklungsumgebung
- **[Sicherheit](Sicherheit)** - Best Practices

---

**API-Dokumentation komplett!** 🎉
