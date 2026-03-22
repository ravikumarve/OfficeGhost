"""
AI Office Pilot - Core Memory Engine
5-layer self-learning system
"""

import json
import sqlite3
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from core.config import Config


class MemoryEngine:
    """
    Self-learning memory with 5 layers:
    1. Feedback Loop
    2. Preference Capture
    3. Style Learning
    4. Behavioral Patterns
    5. Predictive Engine
    """

    def __init__(self):
        self.db_path = str(Config.MEMORY_DB)
        self._init_db()

    def _init_db(self):
        """Create all learning tables"""
        Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Feedback
        c.execute("""CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action_type TEXT NOT NULL,
            action_detail TEXT NOT NULL,
            ai_output TEXT NOT NULL,
            user_feedback TEXT NOT NULL,
            user_correction TEXT,
            context TEXT
        )""")

        # Preferences
        c.execute("""CREATE TABLE IF NOT EXISTS preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            times_confirmed INTEGER DEFAULT 1,
            last_updated TEXT NOT NULL,
            UNIQUE(category, key)
        )""")

        # Writing Samples
        c.execute("""CREATE TABLE IF NOT EXISTS writing_samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            content TEXT NOT NULL,
            recipient TEXT,
            word_count INTEGER
        )""")

        # Style DNA
        c.execute("""CREATE TABLE IF NOT EXISTS style_dna (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trait TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            sample_count INTEGER DEFAULT 0,
            last_updated TEXT NOT NULL
        )""")

        # Action Log
        c.execute("""CREATE TABLE IF NOT EXISTS action_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            day_of_week TEXT NOT NULL,
            hour INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            action_detail TEXT NOT NULL,
            context TEXT,
            sequence_id TEXT
        )""")

        # Score History for Chart
        c.execute("""CREATE TABLE IF NOT EXISTS score_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            score REAL NOT NULL
        )""")

        # Discovered Patterns
        c.execute("""CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT NOT NULL,
            description TEXT NOT NULL,
            trigger_cond TEXT NOT NULL,
            expected_actions TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            times_observed INTEGER DEFAULT 1,
            last_seen TEXT NOT NULL,
            active INTEGER DEFAULT 1
        )""")

        # Contact Memory
        c.execute("""CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            greeting TEXT,
            tone TEXT,
            priority TEXT DEFAULT 'normal',
            forward_to TEXT,
            always_cc TEXT,
            trusted INTEGER DEFAULT 0,
            interaction_count INTEGER DEFAULT 0,
            last_interaction TEXT
        )""")

        # Category Rules
        c.execute("""CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor TEXT NOT NULL,
            category TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            times_used INTEGER DEFAULT 1,
            last_used TEXT NOT NULL,
            UNIQUE(vendor, category)
        )""")

        conn.commit()
        conn.close()

    # ═══ LAYER 1: FEEDBACK ═══

    def record_feedback(
        self, action_type, detail, ai_output, feedback, correction=None, context=None
    ):
        """Record user feedback on AI action"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute(
            """INSERT INTO feedback
            (timestamp, action_type, action_detail, ai_output,
             user_feedback, user_correction, context)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.now().isoformat(),
                action_type,
                detail,
                ai_output,
                feedback,
                correction,
                json.dumps(context) if context else None,
            ),
        )

        conn.commit()
        conn.close()

        # Learn from corrections immediately
        if feedback in ("negative", "edited") and correction:
            self._learn_correction(action_type, detail, ai_output, correction)

    def get_accuracy(self):
        """Get accuracy stats per action type"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("""SELECT action_type,
            COUNT(*) as total,
            SUM(CASE WHEN user_feedback='positive' THEN 1 ELSE 0 END) as good
            FROM feedback GROUP BY action_type""")

        stats = {}
        for row in c.fetchall():
            action, total, good = row
            stats[action] = {
                "total": total,
                "correct": good,
                "accuracy": round(good / total * 100, 1) if total > 0 else 0,
            }

        conn.close()
        return stats

    def _learn_correction(self, action_type, detail, wrong, correct):
        """Immediately learn from user correction"""
        if action_type == "file_categorize":
            self.set_preference("file_category", detail, correct, "correction")
        elif action_type == "data_category":
            self.learn_vendor_category(detail, correct)

    # ═══ LAYER 2: PREFERENCES ═══

    def set_preference(self, category, key, value, source="observed"):
        """Store or update a preference"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        boost = 0.2 if source == "correction" else 0.05

        c.execute(
            """INSERT INTO preferences
            (category, key, value, confidence, times_confirmed, last_updated)
            VALUES (?, ?, ?, ?, 1, ?)
            ON CONFLICT(category, key) DO UPDATE SET
                value = excluded.value,
                confidence = MIN(0.99, preferences.confidence + ?),
                times_confirmed = preferences.times_confirmed + 1,
                last_updated = excluded.last_updated
        """,
            (category, key, value, 0.5 + boost, datetime.now().isoformat(), boost),
        )

        conn.commit()
        conn.close()

    def get_preference(self, category, key, default=None):
        """Get a learned preference"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute(
            """SELECT value, confidence FROM preferences
            WHERE category=? AND key=? AND confidence > 0.4""",
            (category, key),
        )

        result = c.fetchone()
        conn.close()

        return result[0] if result else default

    def get_preferences(self, category):
        """Get all preferences for a category"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute(
            """SELECT key, value, confidence FROM preferences
            WHERE category=? AND confidence > 0.4
            ORDER BY confidence DESC""",
            (category,),
        )

        prefs = {r[0]: {"value": r[1], "confidence": r[2]} for r in c.fetchall()}
        conn.close()
        return prefs

    # ═══ LAYER 2B: CONTACTS ═══

    def learn_contact(self, email: str, **kwargs) -> None:
        """Learn about a contact"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("SELECT id FROM contacts WHERE email=?", (email,))
        exists = c.fetchone()

        if exists:
            updates = []
            params = []
            for field in [
                "name",
                "greeting",
                "tone",
                "priority",
                "forward_to",
                "always_cc",
                "trusted",
            ]:
                if field in kwargs and kwargs[field] is not None:
                    updates.append(f"{field}=?")
                    params.append(kwargs[field])

            updates.append("interaction_count = interaction_count + 1")
            updates.append("last_interaction=?")
            params.append(datetime.now().isoformat())
            params.append(email)

            c.execute(f"UPDATE contacts SET {', '.join(updates)} WHERE email=?", params)
        else:
            c.execute(
                """INSERT INTO contacts
                (email, name, greeting, tone, priority,
                 forward_to, always_cc, trusted, interaction_count, last_interaction)
                VALUES (?,?,?,?,?,?,?,?,1,?)""",
                (
                    email,
                    kwargs.get("name"),
                    kwargs.get("greeting"),
                    kwargs.get("tone"),
                    kwargs.get("priority", "normal"),
                    kwargs.get("forward_to"),
                    kwargs.get("always_cc"),
                    kwargs.get("trusted", 0),
                    datetime.now().isoformat(),
                ),
            )

        conn.commit()
        conn.close()

    def get_contact(self, email: str) -> Optional[dict]:
        """Get contact memory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("SELECT * FROM contacts WHERE email=?", (email,))
        row = c.fetchone()
        conn.close()

        return dict(row) if row else None

    def is_trusted_contact(self, email: str) -> bool:
        """Check if contact is trusted for auto-send"""
        contact = self.get_contact(email)
        if not contact:
            return False
        return bool(contact.get("trusted", 0)) or contact.get("priority") == "trusted"

    def set_trusted_contact(self, email: str, trusted: bool = True) -> None:
        """Mark/unmark contact as trusted"""
        self.learn_contact(email, trusted=1 if trusted else 0)

    def get_all_contacts(self) -> list[dict]:
        """Get all contacts"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("SELECT * FROM contacts ORDER BY interaction_count DESC")
        rows = c.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_trusted_contacts(self) -> list[dict]:
        """Get all trusted contacts"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("SELECT * FROM contacts WHERE trusted=1 ORDER BY name")
        rows = c.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # ═══ LAYER 3: STYLE LEARNING ═══

    def learn_style(self, text: str, recipient: Optional[str] = None) -> None:
        """Analyze and store writing sample"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute(
            """INSERT INTO writing_samples
            (timestamp, content, recipient, word_count)
            VALUES (?,?,?,?)""",
            (datetime.now().isoformat(), text, recipient, len(text.split())),
        )

        conn.commit()
        conn.close()

        # Extract traits
        traits = {}

        # Sentence length
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        if sentences:
            avg = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg < 8:
                traits["sentence_length"] = "very_short"
            elif avg < 15:
                traits["sentence_length"] = "short"
            elif avg < 25:
                traits["sentence_length"] = "medium"
            else:
                traits["sentence_length"] = "long"

        # Formality
        text_l = text.lower()
        informal = sum(1 for w in ["hey", "hi", "thanks", "cool", "awesome", "!"] if w in text_l)
        formal = sum(1 for w in ["dear", "sincerely", "regards", "kindly"] if w in text_l)

        if formal > informal:
            traits["formality"] = "formal"
        elif informal > formal:
            traits["formality"] = "casual"
        else:
            traits["formality"] = "neutral"

        # Greeting
        first_line = text.strip().split("\n")[0].strip()
        if first_line:
            traits["greeting"] = first_line

        # Sign-off
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        for line in reversed(lines[-3:]):
            if any(s in line.lower() for s in ["best", "thanks", "regards", "cheers", "sincerely"]):
                traits["signoff"] = line
                break

        # Store traits
        self._update_style_traits(traits)

    def _update_style_traits(self, traits):
        """Update style DNA table"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        for trait, value in traits.items():
            c.execute(
                """INSERT INTO style_dna
                (trait, value, confidence, sample_count, last_updated)
                VALUES (?,?,0.5,1,?)
                ON CONFLICT(trait) DO UPDATE SET
                    value = CASE
                        WHEN excluded.value = style_dna.value THEN style_dna.value
                        ELSE excluded.value END,
                    confidence = CASE
                        WHEN excluded.value = style_dna.value
                        THEN MIN(0.99, style_dna.confidence + 0.05)
                        ELSE MAX(0.3, style_dna.confidence - 0.1) END,
                    sample_count = style_dna.sample_count + 1,
                    last_updated = excluded.last_updated
            """,
                (trait, value, datetime.now().isoformat()),
            )

        conn.commit()
        conn.close()

    def get_style(self):
        """Get writing style profile"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("""SELECT trait, value, confidence, sample_count
            FROM style_dna ORDER BY confidence DESC""")

        profile = {}
        for row in c.fetchall():
            profile[row[0]] = {"value": row[1], "confidence": row[2], "samples": row[3]}

        conn.close()
        return profile

    def get_style_prompt(self):
        """Generate style instructions for AI"""
        profile = self.get_style()
        if not profile:
            return ""

        parts = ["\n[LEARNED WRITING STYLE]"]

        if "formality" in profile:
            parts.append(f"Tone: {profile['formality']['value']}")
        if "sentence_length" in profile:
            parts.append(f"Sentences: {profile['sentence_length']['value']}")
        if "greeting" in profile:
            parts.append(f"Greeting style: {profile['greeting']['value']}")
        if "signoff" in profile:
            parts.append(f"Sign-off: {profile['signoff']['value']}")

        parts.append("[Match this style closely]")
        return "\n".join(parts)

    # ═══ LAYER 4: BEHAVIORAL PATTERNS ═══

    def log_action(self, action_type, detail, context=None):
        """Log action for pattern discovery"""
        now = datetime.now()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        seq_id = hashlib.md5(
            f"{now.strftime('%Y-%m-%d-%H')}-{now.minute // 2}".encode()
        ).hexdigest()[:8]

        c.execute(
            """INSERT INTO action_log
            (timestamp, day_of_week, hour, action_type,
             action_detail, context, sequence_id)
            VALUES (?,?,?,?,?,?,?)""",
            (
                now.isoformat(),
                now.strftime("%A"),
                now.hour,
                action_type,
                detail,
                json.dumps(context) if context else None,
                seq_id,
            ),
        )

        conn.commit()

        # Discover patterns every 50 actions
        count = c.execute("SELECT COUNT(*) FROM action_log").fetchone()[0]
        conn.close()

        if count % 50 == 0:
            self.discover_patterns()

    def discover_patterns(self):
        """Find recurring behavioral patterns"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Time-based patterns
        c.execute("""SELECT day_of_week, hour, action_type,
            action_detail, COUNT(*) as freq
            FROM action_log
            GROUP BY day_of_week, hour, action_type
            HAVING freq >= 3
            ORDER BY freq DESC""")

        for row in c.fetchall():
            day, hour, action, detail, freq = row
            desc = f"Every {day} ~{hour}:00: {action} ({detail})"
            trigger = json.dumps({"day": day, "hour": hour})
            actions = json.dumps({"action": action, "detail": detail})
            self._store_pattern("time_based", desc, trigger, actions, min(0.95, freq * 0.1))

        # Chain patterns
        c.execute("""SELECT a1.action_type, a2.action_type, COUNT(*) as freq
            FROM action_log a1
            JOIN action_log a2 ON a1.sequence_id = a2.sequence_id
                AND a2.id > a1.id AND a2.id <= a1.id + 3
            WHERE a1.action_type != a2.action_type
            GROUP BY a1.action_type, a2.action_type
            HAVING freq >= 3
            ORDER BY freq DESC""")

        for row in c.fetchall():
            act1, act2, freq = row
            desc = f"After {act1}, usually does {act2}"
            trigger = json.dumps({"after": act1})
            actions = json.dumps({"next": act2})
            self._store_pattern("chain", desc, trigger, actions, min(0.95, freq * 0.1))

        conn.close()

    def _store_pattern(self, ptype, desc, trigger, actions, conf):
        """Store discovered pattern"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute(
            "SELECT id, times_observed, confidence FROM patterns WHERE pattern_type=? AND trigger_cond=?",
            (ptype, trigger),
        )
        existing = c.fetchone()

        if existing:
            c.execute(
                """UPDATE patterns
                SET times_observed=?, confidence=?, last_seen=?
                WHERE id=?""",
                (
                    existing[1] + 1,
                    min(0.99, existing[2] + 0.05),
                    datetime.now().isoformat(),
                    existing[0],
                ),
            )
        else:
            c.execute(
                """INSERT INTO patterns
                (pattern_type, description, trigger_cond,
                 expected_actions, confidence, last_seen)
                VALUES (?,?,?,?,?,?)""",
                (ptype, desc, trigger, actions, conf, datetime.now().isoformat()),
            )

        conn.commit()
        conn.close()

    def get_patterns(self):
        """Get active patterns"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("""SELECT pattern_type, description, trigger_cond,
            expected_actions, confidence, times_observed
            FROM patterns WHERE active=1 AND confidence > 0.5
            ORDER BY confidence DESC""")

        patterns = []
        for row in c.fetchall():
            patterns.append(
                {
                    "type": row[0],
                    "description": row[1],
                    "trigger": json.loads(row[2]),
                    "actions": json.loads(row[3]),
                    "confidence": row[4],
                    "observed": row[5],
                }
            )

        conn.close()
        return patterns

    # ═══ LAYER 5: PREDICTIONS ═══

    def predict(self):
        """Predict next actions based on patterns"""
        predictions = []
        now = datetime.now()
        day = now.strftime("%A")
        hour = now.hour

        for pattern in self.get_patterns():
            if pattern["type"] == "time_based":
                t = pattern["trigger"]
                if t.get("day") == day and abs(t.get("hour", -1) - hour) <= 1:
                    predictions.append(
                        {
                            "type": "time_based",
                            "action": pattern["actions"],
                            "confidence": pattern["confidence"],
                            "message": (
                                f"It's {day} {hour}:00. You usually "
                                f"{pattern['actions'].get('action', '')} now. "
                                f"Should I start?"
                            ),
                        }
                    )

            elif pattern["type"] == "chain":
                recent = self._recent_actions(5)
                for act in recent:
                    if act == pattern["trigger"].get("after"):
                        predictions.append(
                            {
                                "type": "chain",
                                "action": pattern["actions"],
                                "confidence": pattern["confidence"],
                                "message": (
                                    f"You just did {act}. "
                                    f"You usually do {pattern['actions'].get('next', '')} next."
                                ),
                            }
                        )

        predictions.sort(key=lambda x: x["confidence"], reverse=True)
        return [p for p in predictions if p["confidence"] >= 0.7]

    def _recent_actions(self, minutes):
        """Get action types from last N minutes"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        cutoff = (datetime.now() - timedelta(minutes=minutes)).isoformat()
        c.execute("SELECT DISTINCT action_type FROM action_log WHERE timestamp > ?", (cutoff,))
        actions = [r[0] for r in c.fetchall()]
        conn.close()
        return actions

    # ═══ VENDOR CATEGORIES ═══

    def learn_vendor_category(self, vendor, category):
        """Learn vendor → expense category mapping"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute(
            """INSERT INTO categories (vendor, category, last_used)
            VALUES (?,?,?)
            ON CONFLICT(vendor, category) DO UPDATE SET
                times_used = categories.times_used + 1,
                confidence = MIN(0.99, categories.confidence + 0.1),
                last_used = excluded.last_used
        """,
            (vendor.lower(), category, datetime.now().isoformat()),
        )

        conn.commit()
        conn.close()

    def predict_category(self, vendor):
        """Predict expense category for vendor"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute(
            """SELECT category, confidence FROM categories
            WHERE vendor=? ORDER BY confidence DESC LIMIT 1""",
            (vendor.lower(),),
        )

        result = c.fetchone()
        conn.close()

        if result:
            return {"category": result[0], "confidence": result[1]}

        return {"category": None, "confidence": 0}

    # ═══ REPORTING ═══

    def get_learning_report(self):
        """Comprehensive learning progress"""
        accuracy = self.get_accuracy()
        style = self.get_style()
        patterns = self.get_patterns()

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        contacts_count = c.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
        categories_count = c.execute("SELECT COUNT(DISTINCT category) FROM categories").fetchone()[
            0
        ]
        total_actions = c.execute("SELECT COUNT(*) FROM action_log").fetchone()[0]
        total_feedback = c.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
        conn.close()

        # Calculate learning score
        score = 0

        # Feedback volume (max 20)
        score += min(20, total_feedback * 0.5)

        # Accuracy (max 25)
        if accuracy:
            avg_acc = sum(s["accuracy"] for s in accuracy.values()) / len(accuracy)
            score += avg_acc * 0.25

        # Style confidence (max 20)
        if style:
            avg_conf = sum(v["confidence"] for v in style.values()) / len(style)
            score += avg_conf * 20

        # Patterns (max 20)
        score += min(20, len(patterns) * 2)

        # Contacts + Categories (max 15)
        score += min(8, categories_count)
        score += min(7, contacts_count)

        # Get score history for chart and record current score
        history = []
        try:
            # Record current score
            c.execute(
                "INSERT INTO score_history (timestamp, score) VALUES (?, ?)",
                (datetime.now().isoformat(), round(min(100, score), 1))
            )
            conn.commit()
            
            # Get history
            history_data = c.execute(
                "SELECT timestamp, score FROM score_history ORDER BY timestamp DESC LIMIT 20"
            ).fetchall()
            for row in history_data:
                history.append({"date": row[0][:10], "score": row[1]})
            history.reverse()
        except Exception:
            pass
        
        return {
            "learning_score": round(min(100, score), 1),
            "accuracy": accuracy,
            "style_traits": len(style),
            "patterns_found": len(patterns),
            "contacts_learned": contacts_count,
            "categories_learned": categories_count,
            "total_actions": total_actions,
            "total_feedback": total_feedback,
            "patterns": patterns[:10],
            "history": history,
        }
