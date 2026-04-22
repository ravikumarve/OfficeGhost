# GhostOffice - API Documentation

## Base URL

```
http://localhost:5000
```

## Authentication

### Login

**POST** `/login`

Request:
```json
{
  "password": "your_master_password"
}
```

Response (200):
```json
{
  "success": true,
  "message": "Login successful"
}
```

Response (401):
```json
{
  "success": false,
  "message": "Invalid password"
}
```

### Logout

**POST** `/logout`

Response:
```json
{
  "success": true
}
```

---

## Status

### Get System Status

**GET** `/api/status`

Authentication: Required

Response (200):
```json
{
  "health": {
    "ram": {
      "total_gb": 16.0,
      "used_gb": 8.0,
      "available_gb": 8.0,
      "percent": 50,
      "status": "🟢"
    },
    "disk": {
      "total_gb": 500.0,
      "free_gb": 200.0,
      "percent_used": 60,
      "status": "🟢"
    },
    "ollama": {
      "running": true,
      "models_loaded": 1,
      "status": "🟢"
    },
    "overall": "🟢 ALL SYSTEMS GO"
  },
  "security": {
    "overall": "🟢 SECURE",
    "recent_alerts": 0
  },
  "compliance": {
    "overall": "COMPLIANT",
    "checks": [...]
  },
  "queue": {
    "pending": 0,
    "completed": 10,
    "failed": 0,
    "dead_letter": 0
  },
  "encryption": {
    "setup": true,
    "unlocked": true
  }
}
```

---

## Email Operations

### Get Unread Emails

**GET** `/api/emails/unread`

Authentication: Required

Query Parameters:
- `limit` (optional): Number of emails to fetch (default: 10)

Response (200):
```json
{
  "emails": [
    {
      "id": "abc123",
      "from": "sender@example.com",
      "subject": "Email Subject",
      "date": "2026-03-22T10:00:00",
      "body": "Email body...",
      "category": "ROUTINE"
    }
  ],
  "count": 1
}
```

### Send Email Reply

**POST** `/api/emails/send`

Authentication: Required

Request:
```json
{
  "to": "recipient@example.com",
  "subject": "Re: Original Subject",
  "body": "Reply body text...",
  "in_reply_to": "original_message_id"
}
```

Response (200):
```json
{
  "success": true,
  "message": "Email sent successfully"
}
```

---

## File Operations

### Get Watched Files

**GET** `/api/files`

Authentication: Required

Response (200):
```json
{
  "files": [
    {
      "path": "/home/user/Downloads/document.pdf",
      "name": "document.pdf",
      "extension": ".pdf",
      "size": 1024,
      "modified": "2026-03-22T10:00:00"
    }
  ],
  "count": 1
}
```

### Trigger File Scan

**POST** `/api/files/scan`

Authentication: Required

Response (200):
```json
{
  "success": true,
  "files_found": 5
}
```

---

## Learning & Memory

### Get Learning Report

**GET** `/api/learning/report`

Authentication: Required

Response (200):
```json
{
  "learning_score": 75,
  "accuracy": "85%",
  "patterns_found": 12,
  "contacts_learned": 5,
  "categories_learned": 8,
  "total_actions": 150,
  "patterns": [
    {
      "description": "Morning email processing",
      "confidence": 0.9
    }
  ]
}
```

### Get Preferences

**GET** `/api/learning/preferences`

Authentication: Required

Response (200):
```json
{
  "preferences": {
    "preferred_contact_time": "morning",
    "default_category": "ROUTINE",
    "auto_reply_tone": "professional"
  }
}
```

---

## Backup & Export

### Create Backup

**POST** `/api/backup/create`

Authentication: Required

Response (200):
```json
{
  "success": true,
  "backup_path": "/data/backups/backup-20260322.tar.gz"
}
```

### Export Data

**GET** `/api/export`

Authentication: Required

Query Parameters:
- `format`: Export format (json, csv)

Response: File download

---

## Settings

### Get Settings

**GET** `/api/settings`

Authentication: Required

Response (200):
```json
{
  "settings": {
    "watch_folders": ["/home/user/Downloads"],
    "max_emails_per_cycle": 20,
    "auto_lock_minutes": 30,
    "notifications_enabled": true
  }
}
```

### Update Settings

**PUT** `/api/settings`

Authentication: Required

Request:
```json
{
  "watch_folders": ["/home/user/Downloads", "/home/user/Desktop"],
  "max_emails_per_cycle": 30
}
```

Response (200):
```json
{
  "success": true,
  "message": "Settings updated"
}
```

---

## Error Responses

All endpoints may return:

### 400 Bad Request
```json
{
  "error": "Invalid request",
  "message": "Detailed error message"
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "error": "Access denied"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Error details"
}
```

---

## Rate Limiting

The API is rate-limited:
- 60 requests per minute for authenticated users
- 10 requests per minute for unauthenticated requests

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1234567890
```