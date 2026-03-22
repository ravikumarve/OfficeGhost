# TODO.md - GhostOffice v3.0 Improvements

## Phase 1: Testing + Error Handling

### Tests to Add
- [x] `Tests/conftest.py` - Add pytest fixtures for mock IMAP/SMTP servers
- [x] `Tests/test_email_reader.py` - Test EmailReader class
- [x] `Tests/test_email_sender.py` - Test EmailSender class with mock SMTP
- [x] `Tests/test_file_watcher.py` - Test FileWatcher class
- [x] `Tests/test_file_analyzer.py` - Test FileAnalyzer class
- [x] `Tests/test_file_sorter.py` - Test FileSorter class
- [x] `Tests/test_data_extractor.py` - Test DataExtractor class
- [x] `Tests/test_health_monitor.py` - Test HealthMonitor class
- [x] `Tests/test_compliance.py` - Test ComplianceEngine class
- [x] `Tests/test_audit.py` - Test AuditLogger class
- [x] `Tests/test_ollama_brain.py` - Test OllamaBrain with mock server
- [x] `Tests/test_queue_manager.py` - Test QueueManager and Task
- [x] `Tests/test_integration.py` - Add end-to-end integration tests

### Error Handling Fixes
- [x] Error handling improved in `Modules/email_brain/reader.py`
- [x] Error handling improved in `Modules/file_commander/watcher.py`
- [x] Add retry logic with exponential backoff for network operations
- [x] Add dead letter queue for failed operations
- [x] Add proper error logging to all exception handlers

---

## Phase 2: Documentation + Code Quality

### Linting & Type Hints
- [x] Create `pyproject.toml` with ruff configuration
- [x] Add `ruff.toml` for code style rules
- [x] Add type hints to `Modules/email_brain/reader.py`
- [x] Add type hints to `Modules/email_brain/sender.py`
- [x] Add type hints to `Modules/file_commander/watcher.py`
- [x] Add type hints to `Modules/file_commander/analyzer.py`
- [x] Add type hints to `Modules/file_commander/sorter.py`
- [x] Add type hints to `Modules/data_engine/extractor.py`
- [x] Add type hints to `Modules/data_engine/sheet_writer.py`
- [x] Add type hints to `Core/health_monitor.py`
- [x] Add type hints to `Core/queue_manager.py`
- [x] Add type hints to `Core/error_recovery.py`
- [x] Run ruff/ruff format on entire codebase

### Documentation
- [x] Expand `README.md` with architecture diagram (Mermaid)
- [x] Add troubleshooting section to README
- [x] Add deployment guide
- [x] Create `ARCHITECTURE.md` with system design
- [x] Create `API.md` if dashboard exposes endpoints
- [ ] Add docstrings to all public methods

### Pre-commit & CI
- [x] Create `.pre-commit-config.yaml`
- [x] Create `.github/workflows/ci.yml` for GitHub Actions
- [ ] Add `tox.ini` for local testing across Python versions

### Code Quality
- [x] Extract magic numbers from `reader.py`, `watcher.py` to Config
- [ ] Replace print statements with proper logging
- [ ] Standardize error messages format
- [ ] Remove emoji from code/logs (keep in CLI only)

---

## Phase 3: Missing Features

### Email Auto-Send
- [x] Add user confirmation step before sending drafts
- [x] Implement auto-send option for trusted contacts
- [x] Add queue for pending email sends
- [x] Add email template customization

### Meeting/Calendar
- [x] Add MEETING classification handling in `pilot.py`
- [x] Implement ICS calendar parsing
- [x] Add calendar integration (Google Calendar API or local .ics)
- [ ] Meeting response automation

### Notifications
- [x] Implement `Notifications/notifier.py` with plyer
- [x] Add notification preferences to Config
- [x] Add sound notifications option
- [x] Add notification throttling

### CLI Tool
- [x] Implement `Cli/` module with rich CLI
- [x] Add subcommands: status, send, test, configure
- [x] Add interactive mode with rich tables
- [ ] Add shell completion

### Dashboard
- [x] Implement `Dashboard/app.py` Flask app
- [x] Add status endpoint `/api/status`
- [x] Add audit log viewer
- [x] Add settings page
- [x] Add authentication to dashboard

### Test Mode
- [x] Add `--dry-run` flag to main.py
- [x] Add `--test-email` flag to test email processing
- [x] Add `--test-files` flag to test file processing

---

## Phase 4: Operations

### Logging
- [x] Add `Core/logging_config.py` with structured logging
- [x] Add module-level loggers (security, email, files, data, ai, learning, system)
- [ ] Replace print statements in main modules
- [ ] Add log rotation
- [ ] Add log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Docker
- [x] Create `Dockerfile` (multi-stage build)
- [x] Create `docker-compose.yml` (with Ollama optional)
- [x] Create `.dockerignore`
- [ ] Add development vs production Docker configs

### Migrations
- [x] Create `migrations/` directory with `__init__.py`
- [x] Implement migration system for `memory.db` schema changes
- [x] Add migration for trusted contacts table update

### Metrics
- [x] Add `Core/metrics.py` with Prometheus-compatible output
- [x] Add `/api/metrics` endpoint (text/plain)
- [x] Add `/api/metrics/json` endpoint (JSON)
- [ ] Add metrics dashboard integration
- [ ] Add Grafana dashboard config

---

## Phase 5: Security Enhancements

### Authentication
- [x] Add TOTP 2FA support (optional) - `pyotp` based
- [x] Add biometric unlock option (if available)
- [x] Add session management with refresh tokens

### Network
- [x] Add IP allowlisting configuration - `Security/network.py`
- [x] Add network isolation mode
- [x] Add VPN support option

### Rate Limiting
- [x] Add rate limiting middleware for dashboard - `Security/rate_limit.py`
- [x] Add per-endpoint rate limiting
- [x] Add rate limit configuration via .env

---

## Priority Order

1. **Week 1**: Phase 1 - Testing + Error Handling
2. **Week 2**: Phase 2 - Code Quality + Documentation ✅ (IN PROGRESS)
3. **Week 3**: Phase 3 - Missing Features (core)
4. **Week 4**: Phase 3 - Missing Features (CLI, Dashboard)
5. **Week 5**: Phase 4 - Operations
6. **Week 6**: Phase 5 - Security

---

## Commands for Tracking

```bash
# Mark task complete
grep -n "\- \[ \]" TODO.md | head -20  # Show incomplete tasks

# Show progress
grep -c "\- \[ \]" TODO.md && grep -c "\- \[x\]" TODO.md
```
