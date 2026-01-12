# Datenbank-Schema

Übersicht über das Datenbank-Schema von L8teStudy.

---

## 📊 Entity-Relationship-Diagramm

```
┌─────────────┐       ┌─────────────┐
│ SchoolClass │───┐   │    User     │
└─────────────┘   │   └─────────────┘
       │          │          │
       │          └──────────┤
       │                     │
       ├─────────────────────┤
       │                     │
┌──────▼──────┐       ┌──────▼──────┐
│   Subject   │       │    Task     │
└─────────────┘       └─────────────┘
       │                     │
       │              ┌──────┴──────┐
       │              │             │
       │       ┌──────▼──────┐  ┌──▼──────────┐
       │       │ TaskMessage │  │ TaskImage   │
       │       └─────────────┘  └─────────────┘
       │
┌──────▼──────┐
│    Event    │
└─────────────┘
       │
┌──────▼──────┐
│    Grade    │
└─────────────┘
```

---

## 🗄️ Haupttabellen

### SchoolClass (Schulklassen)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | Integer | Primärschlüssel |
| name | String(64) | Klassenname |
| code | String(6) | Login-Code (eindeutig) |
| created_at | DateTime | Erstellungsdatum |
| chat_enabled | Boolean | Chat aktiviert? |

**Beziehungen**:
- `users` → User (1:n)
- `tasks` → Task (1:n)
- `events` → Event (1:n)
- `subjects` → Subject (n:m via subject_classes)

---

### User (Benutzer)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | Integer | Primärschlüssel |
| username | String(64) | Benutzername |
| password_hash | String(256) | Passwort-Hash (PBKDF2) |
| role | String(20) | Rolle (student/admin/super_admin) |
| class_id | Integer | Fremdschlüssel → SchoolClass |
| dark_mode | Boolean | Dark Mode aktiviert? |
| language | String(5) | Sprache (de/en/fr/es/it/tr) |
| needs_password_change | Boolean | Passwort ändern erzwingen? |
| has_seen_tutorial | Boolean | Tutorial gesehen? |
| created_at | DateTime | Erstellungsdatum |

**Beziehungen**:
- `school_class` → SchoolClass (n:1)
- `tasks` → Task (1:n)
- `events` → Event (1:n)
- `grades` → Grade (1:n)
- `notification_settings` → NotificationSetting (1:1)
- `push_subscriptions` → PushSubscription (1:n)

---

### Task (Aufgaben)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | Integer | Primärschlüssel |
| user_id | Integer | Fremdschlüssel → User (Ersteller) |
| class_id | Integer | Fremdschlüssel → SchoolClass |
| subject_id | Integer | Fremdschlüssel → Subject |
| is_shared | Boolean | Klassenübergreifend geteilt? |
| title | String(128) | Titel |
| subject | String(64) | Fach (Legacy) |
| due_date | DateTime | Fälligkeitsdatum |
| description | Text | Beschreibung |
| is_done | Boolean | Erledigt? (deprecated) |
| deleted_at | DateTime | Soft-Delete Zeitstempel |

**Beziehungen**:
- `author` → User (n:1)
- `school_class` → SchoolClass (n:1)
- `subject_rel` → Subject (n:1)
- `images` → TaskImage (1:n)
- `messages` → TaskMessage (1:n)

---

### Event (Termine)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | Integer | Primärschlüssel |
| user_id | Integer | Fremdschlüssel → User |
| class_id | Integer | Fremdschlüssel → SchoolClass |
| subject_id | Integer | Fremdschlüssel → Subject |
| is_shared | Boolean | Geteilt? |
| title | String(128) | Titel |
| date | DateTime | Datum/Zeit |
| description | Text | Beschreibung |
| deleted_at | DateTime | Soft-Delete |

---

### Grade (Noten)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | Integer | Primärschlüssel |
| user_id | Integer | Fremdschlüssel → User |
| subject | String(64) | Fach |
| value | Float | Notenwert |
| weight | Float | Gewichtung |
| title | String(128) | Titel |
| date | DateTime | Datum |
| description | Text | Beschreibung |

**Wichtig**: Noten sind privat, nur für den Benutzer sichtbar!

---

### Subject (Fächer)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | Integer | Primärschlüssel |
| name | String(128) | Fachname |

**Beziehungen**:
- `classes` → SchoolClass (n:m via subject_classes)
- `tasks` → Task (1:n)
- `events` → Event (1:n)

---

## 💬 Chat-Tabellen

### TaskMessage

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | Integer | Primärschlüssel |
| task_id | Integer | Fremdschlüssel → Task |
| user_id | Integer | Fremdschlüssel → User |
| content | Text | Nachrichtentext |
| message_type | String(20) | text/image/file |
| file_url | String(512) | Datei-URL |
| file_name | String(256) | Dateiname |
| created_at | DateTime | Zeitstempel |
| parent_id | Integer | Fremdschlüssel → TaskMessage (Antworten) |

---

### TaskChatRead

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | Integer | Primärschlüssel |
| user_id | Integer | Fremdschlüssel → User |
| task_id | Integer | Fremdschlüssel → Task |
| last_read_at | DateTime | Zuletzt gelesen |

---

## 🔔 Benachrichtigungs-Tabellen

### NotificationSetting

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | Integer | Primärschlüssel |
| user_id | Integer | Fremdschlüssel → User (unique) |
| notify_new_task | Boolean | Neue Aufgaben? |
| notify_new_event | Boolean | Neue Termine? |
| notify_chat_message | Boolean | Chat-Nachrichten? |
| reminder_homework | String(5) | Zeit (HH:MM) oder NULL |
| reminder_exam | String(5) | Zeit (HH:MM) oder NULL |
| last_homework_reminder_at | Date | Letzte Erinnerung |
| last_exam_reminder_at | Date | Letzte Erinnerung |

---

### PushSubscription

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | Integer | Primärschlüssel |
| user_id | Integer | Fremdschlüssel → User |
| endpoint | String(512) | Push-Endpoint (unique) |
| auth_key | String(128) | Auth-Key |
| p256dh_key | String(128) | P256DH-Key |
| created_at | DateTime | Erstellungsdatum |

---

## 🕐 WebUntis-Tabelle

### UntisCredential

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | Integer | Primärschlüssel |
| class_id | Integer | Fremdschlüssel → SchoolClass (unique) |
| server | String(256) | WebUntis-Server |
| school | String(128) | Schulname |
| username | String(128) | Benutzername |
| password | String(512) | Passwort (Fernet-verschlüsselt) |
| untis_class_name | String(64) | Klassenname in WebUntis |

---

## 📝 Weitere Tabellen

### AuditLog

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | Integer | Primärschlüssel |
| user_id | Integer | Fremdschlüssel → User |
| class_id | Integer | Fremdschlüssel → SchoolClass |
| action | String(256) | Aktionsbeschreibung |
| timestamp | DateTime | Zeitstempel |

---

### TaskCompletion

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | Integer | Primärschlüssel |
| user_id | Integer | Fremdschlüssel → User |
| task_id | Integer | Fremdschlüssel → Task |
| is_done | Boolean | Erledigt? |

**Funktion**: Individuelle Erledigungsstatus pro Benutzer

---

### TaskImage

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | Integer | Primärschlüssel |
| task_id | Integer | Fremdschlüssel → Task |
| filename | String(256) | Dateiname |
| created_at | DateTime | Upload-Zeitstempel |

---

### GlobalSetting

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | Integer | Primärschlüssel |
| key | String(64) | Einstellungs-Key (unique) |
| value | Text | Wert |

---

## 🔗 Junction Tables

### subject_classes

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| subject_id | Integer | Fremdschlüssel → Subject |
| class_id | Integer | Fremdschlüssel → SchoolClass |

**Primärschlüssel**: (subject_id, class_id)

**Funktion**: Many-to-Many Beziehung zwischen Fächern und Klassen

---

## 📚 Weitere Ressourcen

- [Architektur](Architektur)
- [API-Dokumentation](API-Dokumentation)
- [Entwicklung](Entwicklung)

---
