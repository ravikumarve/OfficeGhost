# Architecture - GhostOffice v3.0

## System Overview

GhostOffice is a local AI assistant that automates email, file, and data entry tasks while learning user preferences over time.

## Design Principles

1. **100% Local** - All AI processing happens on-device using Ollama
2. **Privacy First** - AES-256 encryption for all stored data
3. **Self-Learning** - 5-layer memory system that improves over time
4. **Resilient** - Transaction-safe operations with recovery
5. **Compliant** - Built-in GDPR/HIPAA support

## Component Architecture

### Core Layer

```
┌─────────────────────────────────────────────────────────────┐
│                      AIOfficePilot                         │
│                    (Main Orchestrator)                      │
├─────────────────────────────────────────────────────────────┤
│  Coordinates all subsystems, manages lifecycle,            │
│  handles user authentication, runs automation cycles       │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌────────────────┐
│  OllamaBrain  │   │  QueueManager   │   │ HealthMonitor  │
│               │   │                 │   │                │
│ Local LLM     │   │ Priority-based  │   │ System health  │
│ interface     │   │ task queue      │   │ monitoring     │
└───────────────┘   └─────────────────┘   └────────────────┘
```

### Security Layer

```
┌─────────────────────────────────────────────────────────────┐
│                     Security Layer                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Encryption  │  │   Access    │  │    AuditLogger      │ │
│  │  Engine    │  │   Control   │  │                     │ │
│  │             │  │             │  │ Hash-chained        │ │
│  │ AES-256    │  │ Password +  │  │ tamper-proof        │ │
│  │ Fernet     │  │ Session mgmt│  │ audit trail         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Threat     │  │   Data      │  │   Compliance        │ │
│  │  Detector   │  │  Lifecycle  │  │     Engine          │ │
│  │             │  │             │  │                     │ │
│  │ Intrusion  │  │ Retention   │  │ GDPR/HIPAA          │ │
│  │ detection   │  │ + deletion  │  │ compliance checks  │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Learning Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    MemoryEngine (5 Layers)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: Feedback Loop                                     │
│  ───────────────────────────────────────                    │
│  Records user corrections, calculates accuracy per          │
│  action type, adjusts behavior based on feedback            │
│                                                             │
│  Layer 2: Preference Capture                                │
│  ───────────────────────────────────────                    │
│  Stores file category preferences, naming conventions,     │
│  contact information with greetings and tone               │
│                                                             │
│  Layer 3: Style Learning                                    │
│  ───────────────────────────────────────                    │
│  Analyzes writing samples, extracts formality, sentence     │
│  length, greeting/signoff patterns                         │
│                                                             │
│  Layer 4: Behavioral Patterns                               │
│  ───────────────────────────────────────                    │
│  Discovers time-based patterns (e.g., "Monday 9am          │
│  check email"), action chains (e.g., "after email          │
│  usually sort files")                                      │
│                                                             │
│  Layer 5: Predictive Engine                                 │
│  ───────────────────────────────────────                    │
│  Generates actionable predictions based on patterns,        │
│  confidence thresholds, recent activity                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Feature Modules

```
┌─────────────────────────────────────────────────────────────┐
│                      Feature Modules                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Email Module              File Module           Data Module│
│  ───────────────          ───────────          ─────────── │
│  ┌───────────────┐        ┌───────────┐       ┌──────────┐│
│  │ EmailReader   │        │FileWatcher│       │DataExtrac││
│  │               │        │           │       │          ││
│  │ IMAP fetch    │        │ watchdog  │       │ AI-based ││
│  │ Parse emails  │        │ + polling │       │ extraction││
│  │ Attachments   │        └─────┬─────┘       └────┬─────┘│
│  └───────┬───────┘              │                 │      │
│          │               ┌──────▼──────┐     ┌─────▼─────┐ │
│          │               │FileAnalyzer │     │ Validator │ │
│          │               │             │     │           │ │
│          │               │ PDF/text/   │     │ Confidence│ │
│          │               │ docx/xlsx   │     │ checks    │ │
│          │               └──────┬──────┘     └───────────┘ │
│          │                      │                           │
│  ┌───────▼───────┐        ┌────▼────┐                     │
│  │ EmailSender   │        │FileSorter│                    │
│  │               │        │          │                    │
│  │ SMTP send     │        │ Category │                    │
│  │ Rate limiting │        │ folders  │                    │
│  └───────────────┘        └──────────┘                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Email Processing Cycle

```
1. Fetch unread emails (IMAP)
           │
           ▼
2. For each email:
   ├── Security check (ThreatDetector)
   ├── Audit log read
   ├── Get contact memory
   ├── Classify with AI (Ollama)
   │         │
   │         ├── SPAM → Archive
   │         ├── URGENT → Notify user
   │         ├── ROUTINE/MEETING → Draft reply
   │         ├── HAS_ATTACHMENT → Process attachments
   │         └── INVOICE → Extract + enter data
   │
   ├── Update contact memory
   ├── Log action for patterns
   └── Audit log write
```

### File Processing Cycle

```
1. Scan watch folders for new files
           │
           ▼
2. For each new file:
   ├── Security check
   ├── Analyze content (PDF/text/docx)
   ├── Get learned category preference
   │         │
   │         ├── Found → Use learned
   │         └── Not found → AI classify
   ├── Generate smart filename
   ├── Get destination folder
   ├── Move file (tracked for recovery)
   ├── If invoice/receipt → Extract data
   └── Record feedback for learning
```

## Security Architecture

### Encryption Flow

```
Master Password
      │
      ▼
┌─────────────┐
│   PBKDF2   │ (600K iterations, 32-byte salt)
│  Key Derive │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   AES-256   │ Fernet symmetric encryption
│   Fernet    │
└──────┬──────┘
       │
       ▼
  Encrypted Data (stored on disk)
```

### Audit Chain

```
┌──────────────────────────────────────────────────────────────┐
│  Entry 1 (Genesis)                                           │
│  hash = SHA256(id + timestamp + action + previous_hash)     │
├──────────────────────────────────────────────────────────────┤
│  Entry 2                                                     │
│  hash = SHA256(id + timestamp + action + Entry1.hash)       │
├──────────────────────────────────────────────────────────────┤
│  Entry 3                                                     │
│  hash = SHA256(id + timestamp + action + Entry2.hash)       │
├──────────────────────────────────────────────────────────────┤
│  ...                                                         │
│                                                              │
│  Verification: Recompute all hashes, compare to stored       │
└──────────────────────────────────────────────────────────────┘
```

## Configuration

All configuration is loaded from `.env` via python-dotenv:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | localhost:11434 | Ollama server URL |
| `OLLAMA_MODEL` | phi3:mini | Default LLM model |
| `MAX_EMAILS_PER_CYCLE` | 50 | Max emails to process |
| `MAX_FILES_PER_CYCLE` | 30 | Max files to process |
| `AUTO_LOCK_MINUTES` | 30 | Auto-lock timeout |
| `ENABLE_GDPR` | false | Enable GDPR compliance |
| `ENABLE_HIPAA` | false | Enable HIPAA compliance |

## Error Recovery

Operations are tracked with a recovery journal:

1. **begin_operation** - Record operation start
2. **add_rollback** - Register rollback actions
3. **complete_operation** - Mark success
4. **fail_operation** - Execute rollback on failure

On restart, incomplete operations are automatically rolled back.
