"""
Persistent LeadHunter database layer.

Supports:
- Supabase PostgreSQL through DATABASE_URL
- SQLite fallback for local development

The public Database API is kept compatible with the existing
LeadHunter pipeline so other modules do not need to be rewritten.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3

from dotenv import load_dotenv

load_dotenv()
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import state_machine as sm
from .errors import NotFoundError, StateTransitionError
from .log import get_logger
from .models import Lead, utcnow_iso

log = get_logger("db")


# ---------------------------------------------------------------------------
# PostgreSQL / SQLite compatibility helpers
# ---------------------------------------------------------------------------

class DBRow(Mapping):
    """
    Small compatibility wrapper.

    Allows both:

        row["id"]

    and:

        row[0]

    so existing LeadHunter code can continue working.
    """

    def __init__(self, columns: List[str], values: tuple):
        self._columns = list(columns)
        self._values = tuple(values)
        self._map = dict(zip(self._columns, self._values))

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return self._map[key]

    def __iter__(self):
        return iter(self._columns)

    def __len__(self):
        return len(self._columns)

    def keys(self):
        return self._map.keys()


class DBCursor:
    """Cursor wrapper compatible with the existing code."""

    def __init__(self, cursor, postgres: bool):
        self.cursor = cursor
        self.postgres = postgres

    @property
    def lastrowid(self):
        """
        SQLite supports lastrowid.

        PostgreSQL does not. PostgreSQL inserts use RETURNING id
        and therefore this is only kept for compatibility.
        """
        if self.postgres:
            return None
        return self.cursor.lastrowid

    def fetchone(self):
        row = self.cursor.fetchone()

        if row is None:
            return None

        if isinstance(row, sqlite3.Row):
            return row

        columns = [desc.name for desc in self.cursor.description]
        return DBRow(columns, tuple(row))

    def fetchall(self):
        rows = self.cursor.fetchall()

        if not rows:
            return []

        if isinstance(rows[0], sqlite3.Row):
            return rows

        columns = [desc.name for desc in self.cursor.description]

        return [
            DBRow(columns, tuple(row))
            for row in rows
        ]

    def __iter__(self):
        return iter(self.fetchall())


class DBConnection:
    """
    Compatibility connection.

    Existing code mostly uses:

        db.conn.execute(sql, params)

    SQLite uses ? placeholders.

    PostgreSQL uses %s placeholders.

    This wrapper translates the common cases automatically.
    """

    _named_parameter = re.compile(
        r"(?<!:):([A-Za-z_][A-Za-z0-9_]*)"
    )

    def __init__(self, raw_connection, postgres: bool):
        self.raw = raw_connection
        self.postgres = postgres

    def _prepare(self, sql: str, params):
        if not self.postgres:
            return sql, params

        # Named parameters:
        #
        # :name
        #
        # become:
        #
        # %s
        #
        # and the dictionary becomes a tuple in matching order.

        if isinstance(params, Mapping):
            names = []

            def replace(match):
                names.append(match.group(1))
                return "%s"

            sql = self._named_parameter.sub(replace, sql)

            return sql, tuple(params[name] for name in names)

        # SQLite positional:
        #
        # ?
        #
        # PostgreSQL:
        #
        # %s

        sql = sql.replace("?", "%s")

        return sql, params

    def execute(self, sql: str, params=()):
        sql, params = self._prepare(sql, params)

        cursor = self.raw.cursor()

        cursor.execute(sql, params)

        return DBCursor(cursor, self.postgres)

    def commit(self):
        self.raw.commit()

    def rollback(self):
        self.raw.rollback()

    def close(self):
        self.raw.close()


# ---------------------------------------------------------------------------
# PostgreSQL schema
# ---------------------------------------------------------------------------

POSTGRES_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id BIGSERIAL PRIMARY KEY,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    city TEXT NOT NULL,
    category TEXT NOT NULL,
    params_json TEXT,
    status TEXT NOT NULL DEFAULT 'RUNNING',
    stats_json TEXT
);

CREATE TABLE IF NOT EXISTS leads (
    id BIGSERIAL PRIMARY KEY,
    external_id TEXT,
    source TEXT NOT NULL,
    run_id BIGINT,
    name TEXT NOT NULL,
    category TEXT,
    city TEXT,
    address TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    phone TEXT,
    phone_normalized TEXT,
    email TEXT,
    website TEXT,
    website_verified TEXT,
    website_status TEXT,
    rating DOUBLE PRECISION,
    reviews_count INTEGER,
    tags_json TEXT DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'DISCOVERED',
    score DOUBLE PRECISION,
    score_reasons_json TEXT DEFAULT '[]',
    lead_tier TEXT,
    qualified INTEGER DEFAULT 0,
    qualification_notes TEXT DEFAULT '',
    site_profile_json TEXT DEFAULT '{}',
    personalized_message TEXT,
    email_subject TEXT,
    email_message TEXT,
    whatsapp_message TEXT,
    demo_url TEXT,
    demo_path TEXT,
    demo_status TEXT,
    outreach_channel TEXT,
    outreach_status TEXT,
    fingerprint TEXT UNIQUE,
    stage_status TEXT,
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    last_contacted_at TEXT,
    next_followup_due TEXT,
    followup_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES runs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_leads_status
    ON leads(status);

CREATE INDEX IF NOT EXISTS idx_leads_run
    ON leads(run_id);

CREATE INDEX IF NOT EXISTS idx_leads_city
    ON leads(city);

CREATE INDEX IF NOT EXISTS idx_leads_external_id
    ON leads(external_id);


CREATE TABLE IF NOT EXISTS lead_events (
    id BIGSERIAL PRIMARY KEY,
    lead_id BIGINT,
    run_id BIGINT,
    ts TEXT NOT NULL,
    from_status TEXT,
    to_status TEXT,
    stage TEXT,
    level TEXT DEFAULT 'INFO',
    event TEXT NOT NULL,
    FOREIGN KEY(lead_id) REFERENCES leads(id) ON DELETE CASCADE,
    FOREIGN KEY(run_id) REFERENCES runs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_events_lead
    ON lead_events(lead_id);

CREATE INDEX IF NOT EXISTS idx_events_run
    ON lead_events(run_id);


CREATE TABLE IF NOT EXISTS kv (
    key TEXT PRIMARY KEY,
    value TEXT
);


CREATE TABLE IF NOT EXISTS approvals (
    approval_id BIGSERIAL PRIMARY KEY,
    lead_id BIGINT NOT NULL UNIQUE,
    business_name TEXT NOT NULL,
    lead_score DOUBLE PRECISION,
    lead_tier TEXT,
    email_message TEXT,
    whatsapp_message TEXT,
    demo_url TEXT,
    website_status TEXT,
    approval_status TEXT NOT NULL DEFAULT 'PENDING_APPROVAL',
    reviewed_at TEXT,
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(lead_id) REFERENCES leads(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_approvals_lead
    ON approvals(lead_id);

CREATE INDEX IF NOT EXISTS idx_approvals_status
    ON approvals(approval_status);
"""


# ---------------------------------------------------------------------------
# SQLite schema
# ---------------------------------------------------------------------------

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    city TEXT NOT NULL,
    category TEXT NOT NULL,
    params_json TEXT,
    status TEXT NOT NULL DEFAULT 'RUNNING',
    stats_json TEXT
);

CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT,
    source TEXT NOT NULL,
    run_id INTEGER,
    name TEXT NOT NULL,
    category TEXT,
    city TEXT,
    address TEXT,
    lat REAL,
    lon REAL,
    phone TEXT,
    phone_normalized TEXT,
    email TEXT,
    website TEXT,
    website_verified TEXT,
    website_status TEXT,
    rating REAL,
    reviews_count INTEGER,
    tags_json TEXT DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'DISCOVERED',
    score REAL,
    score_reasons_json TEXT DEFAULT '[]',
    lead_tier TEXT,
    qualified INTEGER DEFAULT 0,
    qualification_notes TEXT DEFAULT '',
    site_profile_json TEXT DEFAULT '{}',
    personalized_message TEXT,
    email_subject TEXT,
    email_message TEXT,
    whatsapp_message TEXT,
    demo_url TEXT,
    demo_path TEXT,
    demo_status TEXT,
    outreach_channel TEXT,
    outreach_status TEXT,
    fingerprint TEXT UNIQUE,
    stage_status TEXT,
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    last_contacted_at TEXT,
    next_followup_due TEXT,
    followup_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_leads_status
    ON leads(status);

CREATE INDEX IF NOT EXISTS idx_leads_run
    ON leads(run_id);

CREATE TABLE IF NOT EXISTS lead_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    run_id INTEGER,
    ts TEXT NOT NULL,
    from_status TEXT,
    to_status TEXT,
    stage TEXT,
    level TEXT DEFAULT 'INFO',
    event TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_lead
    ON lead_events(lead_id);

CREATE INDEX IF NOT EXISTS idx_events_run
    ON lead_events(run_id);

CREATE TABLE IF NOT EXISTS kv (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS approvals (
    approval_id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL UNIQUE,
    business_name TEXT NOT NULL,
    lead_score REAL,
    lead_tier TEXT,
    email_message TEXT,
    whatsapp_message TEXT,
    demo_url TEXT,
    website_status TEXT,
    approval_status TEXT NOT NULL DEFAULT 'PENDING_APPROVAL',
    reviewed_at TEXT,
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(lead_id) REFERENCES leads(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_approvals_lead
    ON approvals(lead_id);

CREATE INDEX IF NOT EXISTS idx_approvals_status
    ON approvals(approval_status);
"""


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DEFAULT_DATABASE_URL = "postgresql://postgres.hljpzgoduyzitiulmilm:SainiAnhad2224455@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"

class Database:

    def __init__(self, path: Path | str | None = None):

        self.postgres = False

        database_url = (os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL).strip()
        if not os.getenv("DATABASE_URL"):
            os.environ["DATABASE_URL"] = database_url

        # ---------------------------------------------------------------
        # SUPABASE / POSTGRESQL
        # ---------------------------------------------------------------

        is_default_file = (
            path is None
            or str(path).replace("\\", "/").endswith("leadhunter.db")
        )

        if is_default_file and database_url.startswith(
            ("postgresql://", "postgres://")
        ):

            try:
                import psycopg
            except ImportError as exc:
                raise RuntimeError(
                    "PostgreSQL driver is missing. "
                    "Install it with: pip install 'psycopg[binary]'"
                ) from exc

            self.postgres = True
            self.path = database_url

            try:
                raw_connection = psycopg.connect(database_url)
            except Exception as exc:
                raise RuntimeError(
                    "Could not connect to PostgreSQL/Supabase. "
                    "Check DATABASE_URL, database password, host, "
                    "port and network access."
                ) from exc

            self.conn = DBConnection(
                raw_connection,
                postgres=True,
            )

        # ---------------------------------------------------------------
        # SQLITE FALLBACK
        # ---------------------------------------------------------------

        else:

            db_path = str(
                path
                or os.getenv(
                    "LEADHUNTER_DB_PATH",
                    "data/leadhunter.db",
                )
            )

            if db_path != ":memory:":
                Path(db_path).parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

            raw_connection = sqlite3.connect(
                db_path,
                timeout=60.0,
                check_same_thread=False,
            )

            raw_connection.row_factory = sqlite3.Row

            self.path = db_path

            self.conn = DBConnection(
                raw_connection,
                postgres=False,
            )

            try:
                self.conn.execute(
                    "PRAGMA busy_timeout = 60000"
                )

                self.conn.execute(
                    "PRAGMA journal_mode = WAL"
                )

                self.conn.execute(
                    "PRAGMA synchronous = NORMAL"
                )

                self.conn.execute(
                    "PRAGMA cache_size = -64000"
                )

                self.conn.execute(
                    "PRAGMA foreign_keys = ON"
                )

            except Exception:
                pass

        self.init_schema()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def init_schema(self) -> None:

        schema = (
            POSTGRES_SCHEMA
            if self.postgres
            else SQLITE_SCHEMA
        )

        # PostgreSQL does not support executescript.
        # Execute each statement separately.

        statements = [
            statement.strip()
            for statement in schema.split(";")
            if statement.strip()
        ]

        for statement in statements:
            self.conn.execute(statement)

        self.conn.commit()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:

        try:
            self.conn.close()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Runs
    # ------------------------------------------------------------------

    def start_run(
        self,
        city: str,
        category: str,
        params: Dict[str, Any],
    ) -> int:

        if self.postgres:

            cur = self.conn.execute(
                """
                INSERT INTO runs
                    (started_at, city, category, params_json)
                VALUES
                    (%s, %s, %s, %s)
                RETURNING id
                """,
                (
                    utcnow_iso(),
                    city,
                    category,
                    json.dumps(params, default=str),
                ),
            )

            row = cur.fetchone()

            self.conn.commit()

            return int(row["id"])

        cur = self.conn.execute(
            """
            INSERT INTO runs
                (started_at, city, category, params_json)
            VALUES
                (?, ?, ?, ?)
            """,
            (
                utcnow_iso(),
                city,
                category,
                json.dumps(params, default=str),
            ),
        )

        self.conn.commit()

        if cur.lastrowid is not None:
            return int(cur.lastrowid)

        run_row = self.conn.execute("SELECT MAX(id) AS id FROM runs").fetchone()
        return int(run_row["id"]) if run_row and run_row["id"] is not None else 1

    def end_run(
        self,
        run_id: int,
        status: str,
        stats: Dict[str, Any],
    ) -> None:

        self.conn.execute(
            """
            UPDATE runs
            SET
                finished_at=?,
                status=?,
                stats_json=?
            WHERE id=?
            """,
            (
                utcnow_iso(),
                status,
                json.dumps(stats, default=str),
                run_id,
            ),
        )

        self.conn.commit()

    def get_run(self, run_id: int) -> Dict[str, Any]:

        row = self.conn.execute(
            "SELECT * FROM runs WHERE id=?",
            (run_id,),
        ).fetchone()

        if row is None:
            raise NotFoundError(
                f"run {run_id} not found"
            )

        return dict(row)

    def list_runs(
        self,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:

        rows = self.conn.execute(
            """
            SELECT *
            FROM runs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Leads
    # ------------------------------------------------------------------

    def insert_lead(
        self,
        lead: Lead,
    ) -> Tuple[int, bool]:

        row = lead.to_row()

        if row["fingerprint"]:

            existing = self.conn.execute(
                """
                SELECT id
                FROM leads
                WHERE fingerprint=?
                """,
                (row["fingerprint"],),
            ).fetchone()

            if existing:
                return int(existing["id"]), False

        columns = """
            external_id,
            source,
            run_id,
            name,
            category,
            city,
            address,
            lat,
            lon,
            phone,
            phone_normalized,
            email,
            website,
            website_verified,
            website_status,
            rating,
            reviews_count,
            tags_json,
            status,
            score,
            score_reasons_json,
            lead_tier,
            qualified,
            qualification_notes,
            site_profile_json,
            personalized_message,
            email_subject,
            email_message,
            whatsapp_message,
            demo_url,
            demo_path,
            outreach_channel,
            outreach_status,
            fingerprint,
            stage_status,
            retry_count,
            last_error,
            created_at,
            updated_at
        """

        if self.postgres:

            values = [
                row.get(column.strip())
                for column in columns.split(",")
            ]

            placeholders = ", ".join(
                ["%s"] * len(values)
            )

            cur = self.conn.execute(
                f"""
                INSERT INTO leads ({columns})
                VALUES ({placeholders})
                RETURNING id
                """,
                tuple(values),
            )

            result = cur.fetchone()

            self.conn.commit()

            return int(result["id"]), True

        cur = self.conn.execute(
            f"""
            INSERT INTO leads ({columns})
            VALUES (
                :external_id,
                :source,
                :run_id,
                :name,
                :category,
                :city,
                :address,
                :lat,
                :lon,
                :phone,
                :phone_normalized,
                :email,
                :website,
                :website_verified,
                :website_status,
                :rating,
                :reviews_count,
                :tags_json,
                :status,
                :score,
                :score_reasons_json,
                :lead_tier,
                :qualified,
                :qualification_notes,
                :site_profile_json,
                :personalized_message,
                :email_subject,
                :email_message,
                :whatsapp_message,
                :demo_url,
                :demo_path,
                :outreach_channel,
                :outreach_status,
                :fingerprint,
                :stage_status,
                :retry_count,
                :last_error,
                :created_at,
                :updated_at
            )
            """,
            row,
        )

        self.conn.commit()

        if cur.lastrowid is not None:
            return int(cur.lastrowid), True

        lead_row = self.conn.execute("SELECT id FROM leads WHERE fingerprint = ?", (fp,)).fetchone()
        if lead_row:
            return int(lead_row["id"]), True

        lead_max = self.conn.execute("SELECT MAX(id) AS id FROM leads").fetchone()
        return (int(lead_max["id"]) if lead_max and lead_max["id"] is not None else 1), True

    def get_lead(
        self,
        lead_id: int,
    ) -> Lead:

        row = self.conn.execute(
            "SELECT * FROM leads WHERE id=?",
            (lead_id,),
        ).fetchone()

        if row is None:
            raise NotFoundError(
                f"lead {lead_id} not found"
            )

        return Lead.from_row(dict(row))

    def get_lead_by_fingerprint(
        self,
        fingerprint: str,
    ) -> Optional[Lead]:

        row = self.conn.execute(
            """
            SELECT *
            FROM leads
            WHERE fingerprint=?
            """,
            (fingerprint,),
        ).fetchone()

        return (
            Lead.from_row(dict(row))
            if row
            else None
        )

    def get_leads_by_status(
        self,
        status: str,
        limit: int = 100,
    ) -> List[Lead]:

        rows = self.conn.execute(
            """
            SELECT *
            FROM leads
            WHERE status=?
            ORDER BY id
            LIMIT ?
            """,
            (status, limit),
        ).fetchall()

        return [
            Lead.from_row(dict(row))
            for row in rows
        ]

    def get_leads_by_statuses(
        self,
        statuses: List[str],
        city: Optional[str] = None,
        limit: int = 100,
    ) -> List[Lead]:

        if not statuses:
            return []

        city_clause = ""
        params = list(statuses)

        if city:
            city_clause = " AND city LIKE ?"
            params.append(f"%{city}%")

        params.append(limit)

        marks = ",".join(
            ["?"] * len(statuses)
        )

        rows = self.conn.execute(
            f"""
            SELECT *
            FROM leads
            WHERE status IN ({marks}){city_clause}
            ORDER BY id
            LIMIT ?
            """,
            tuple(params),
        ).fetchall()

        return [
            Lead.from_row(dict(row))
            for row in rows
        ]

    def get_lead_ids_by_status(
        self,
        status: str,
        limit: int = 100,
    ) -> List[int]:

        rows = self.conn.execute(
            """
            SELECT id
            FROM leads
            WHERE status=?
            ORDER BY id
            LIMIT ?
            """,
            (status, limit),
        ).fetchall()

        return [
            int(row["id"])
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Resumability
    # ------------------------------------------------------------------

    def get_resumable_leads(
        self,
        stage: str,
        city: Optional[str] = None,
        limit: int = 100,
    ) -> List[Lead]:

        stage_lower = stage.lower().strip()

        city_clause = (
            " AND LOWER(COALESCE(city, '')) LIKE LOWER(?)"
            if city
            else ""
        )

        # ---------------------------------------------------------------
        # WEBSITE VERIFICATION
        # ---------------------------------------------------------------

        if stage_lower in (
            "verification",
            "website_checker",
            "verify",
        ):

            query = (
                "SELECT * FROM leads "
                "WHERE status IN ('DISCOVERED','ENRICHED') "
                "AND (website_status IS NULL "
                "OR website_status='')"
                f"{city_clause} "
                "ORDER BY id ASC LIMIT ?"
            )

        # ---------------------------------------------------------------
        # SCORING
        # ---------------------------------------------------------------

        elif stage_lower in (
            "scoring",
            "lead_scorer",
            "qualify",
        ):

            query = (
                "SELECT * FROM leads "
                "WHERE status='VERIFIED' "
                "AND (score IS NULL OR lead_tier IS NULL)"
                f"{city_clause} "
                "ORDER BY id ASC LIMIT ?"
            )

        # ---------------------------------------------------------------
        # AI PERSONALIZATION
        # ---------------------------------------------------------------

        elif stage_lower in (
            "personalization",
            "personalizer",
            "ai",
        ):

            query = (
                "SELECT * FROM leads "
                "WHERE ("
                "status='QUALIFIED' "
                "OR qualified=1"
                ") "
                "AND UPPER(COALESCE(lead_tier, '')) "
                "IN ('HOT','WARM') "
                "AND ("
                "email_message IS NULL "
                "OR TRIM(email_message)=''"
                ") "
                f"{city_clause} "
                "ORDER BY id ASC LIMIT ?"
            )

        # ---------------------------------------------------------------
        # DEMO GENERATION
        # ---------------------------------------------------------------

        elif stage_lower in (
            "demo",
            "url_generator",
            "demo_generator",
        ):

            query = (
                "SELECT * FROM leads "
                "WHERE status='PERSONALIZED' "
                "AND (demo_status IS NULL "
                "OR demo_status!='READY')"
                f"{city_clause} "
                "ORDER BY id ASC LIMIT ?"
            )

        # ---------------------------------------------------------------
        # APPROVAL
        # ---------------------------------------------------------------

        elif stage_lower in (
            "approval",
            "approval_queue",
            "approval_viewer",
        ):

            query = (
                "SELECT * FROM leads "
                "WHERE status IN "
                "('DEMO_READY','PENDING_APPROVAL') "
                "AND status NOT IN "
                "('APPROVED','REJECTED','SENT','DO_NOT_CONTACT')"
                f"{city_clause} "
                "ORDER BY id ASC LIMIT ?"
            )

        # ---------------------------------------------------------------
        # OUTREACH
        # ---------------------------------------------------------------

        elif stage_lower in (
            "outreach",
            "email_sender",
            "whatsapp_sender",
        ):

            query = (
                "SELECT * FROM leads "
                "WHERE status='APPROVED' "
                "AND (outreach_status IS NULL "
                "OR outreach_status NOT IN "
                "('SENT','DRY_RUN_SENT'))"
                f"{city_clause} "
                "ORDER BY id ASC LIMIT ?"
            )

        # ---------------------------------------------------------------
        # GENERIC
        # ---------------------------------------------------------------

        else:

            query = (
                "SELECT * FROM leads "
                f"WHERE 1=1{city_clause} "
                "ORDER BY id ASC LIMIT ?"
            )

        params = []

        if city:
            params.append(f"%{city}%")

        params.append(limit)

        rows = self.conn.execute(
            query,
            tuple(params),
        ).fetchall()

        return [
            Lead.from_row(dict(row))
            for row in rows
        ]
    def is_stage_completed(
        self,
        lead_id: int,
        stage: str,
    ) -> bool:

        lead = self.get_lead(lead_id)

        stage_lower = stage.lower().strip()

        if stage_lower in (
            "verification",
            "website_checker",
        ):
            return bool(lead.website_status)

        if stage_lower in (
            "scoring",
            "lead_scorer",
        ):
            return (
                lead.score is not None
                and lead.lead_tier is not None
            )

        if stage_lower in (
            "personalization",
            "personalizer",
        ):
            return bool(lead.email_message)

        if stage_lower in (
            "demo",
            "url_generator",
        ):
            return bool(lead.demo_url)

        if stage_lower in (
            "approval",
            "approval_gate",
        ):
            tags = lead.tags or {}

            return (
                lead.status in (
                    sm.LeadStatus.APPROVED,
                    sm.LeadStatus.REJECTED,
                )
                or tags.get("approval_status")
                in ("APPROVED", "REJECTED")
            )

        if stage_lower in (
            "outreach",
            "email",
            "whatsapp",
        ):
            tags = lead.tags or {}

            return (
                lead.status in (
                    sm.LeadStatus.SENT,
                    sm.LeadStatus.DRY_RUN_SENT,
                )
                or tags.get("whatsapp_status") == "SENT"
                or tags.get("email_status") == "SENT"
            )

        return False

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update_lead(
        self,
        lead_id: int,
        fields: Dict[str, Any],
    ) -> None:

        if not fields:
            return

        allowed_columns = {
            "external_id",
            "source",
            "run_id",
            "name",
            "category",
            "city",
            "address",
            "lat",
            "lon",
            "phone",
            "phone_normalized",
            "email",
            "website",
            "website_verified",
            "website_status",
            "rating",
            "reviews_count",
            "tags_json",
            "status",
            "score",
            "score_reasons_json",
            "lead_tier",
            "qualified",
            "qualification_notes",
            "site_profile_json",
            "personalized_message",
            "email_subject",
            "email_message",
            "whatsapp_message",
            "demo_url",
            "demo_path",
            "demo_status",
            "outreach_channel",
            "outreach_status",
            "fingerprint",
            "stage_status",
            "retry_count",
            "last_error",
            "last_contacted_at",
            "next_followup_due",
            "followup_count",
            "created_at",
            "updated_at",
        }

        invalid = set(fields) - allowed_columns

        if invalid:
            raise ValueError(
                f"Invalid lead fields: {sorted(invalid)}"
            )

        fields = dict(fields)

        fields["updated_at"] = utcnow_iso()

        assignments = ", ".join(
            f"{key}=?"
            for key in fields
        )

        self.conn.execute(
            f"""
            UPDATE leads
            SET {assignments}
            WHERE id=?
            """,
            (
                *fields.values(),
                lead_id,
            ),
        )

        self.conn.commit()

    # ------------------------------------------------------------------
    # State transition
    # ------------------------------------------------------------------

    def transition(
        self,
        lead_id: int,
        to_status: str,
        *,
        run_id: Optional[int] = None,
        stage: str = "",
        event: str = "",
        level: str = "INFO",
        extra_fields: Optional[Dict[str, Any]] = None,
    ) -> None:

        lead = self.get_lead(lead_id)

        from_status = lead.status.value

        if from_status == to_status:
            return

        sm.assert_transition(
            from_status,
            to_status,
        )

        fields: Dict[str, Any] = {
            "status": to_status
        }

        if to_status == "FAILED":

            fields["stage_status"] = (
                stage or from_status
            )

            fields["retry_count"] = (
                lead.retry_count + 1
            )

            fields["last_error"] = event

        elif to_status != "FAILED":

            fields["stage_status"] = None

            if to_status == "DISCARDED":
                fields["last_error"] = None

        if extra_fields:
            fields.update(extra_fields)

        self.update_lead(
            lead_id,
            fields,
        )

        self.record_event(
            lead_id=lead_id,
            run_id=run_id,
            from_status=from_status,
            to_status=to_status,
            stage=stage,
            event=event,
            level=level,
        )

    # ------------------------------------------------------------------
    # Failed lead recovery
    # ------------------------------------------------------------------

    def recover_failed(
        self,
        max_retries: int,
    ) -> List[int]:

        rows = self.conn.execute(
            """
            SELECT id, stage_status,
                   retry_count, last_error
            FROM leads
            WHERE status='FAILED'
            """
        ).fetchall()

        recovered: List[int] = []

        from .retry import is_retryable

        for row in rows:

            if row["retry_count"] >= max_retries:
                continue

            try:

                error_obj = (
                    json.loads(row["last_error"])
                    if row["last_error"]
                    else None
                )

                retryable = (
                    bool(error_obj.get("retryable"))
                    if isinstance(error_obj, dict)
                    else True
                )

            except (
                ValueError,
                TypeError,
                AttributeError,
            ):
                retryable = True

            if not retryable:
                continue

            target = (
                row["stage_status"]
                or "DISCOVERED"
            )

            try:
                sm.assert_transition(
                    "FAILED",
                    target,
                )
            except StateTransitionError:
                continue

            self.conn.execute(
                """
                UPDATE leads
                SET status=?,
                    stage_status=NULL
                WHERE id=?
                """,
                (
                    target,
                    row["id"],
                ),
            )

            self.conn.commit()

            self.record_event(
                lead_id=row["id"],
                from_status="FAILED",
                to_status=target,
                stage="recovery",
                event=(
                    "retryable failure - "
                    "re-promoted for retry"
                ),
                level="WARN",
            )

            recovered.append(
                int(row["id"])
            )

        return recovered

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def record_event(
        self,
        *,
        lead_id: Optional[int] = None,
        run_id: Optional[int] = None,
        from_status: Optional[str] = None,
        to_status: Optional[str] = None,
        stage: str = "",
        event: str = "",
        level: str = "INFO",
    ) -> None:

        self.conn.execute(
            """
            INSERT INTO lead_events
                (
                    lead_id,
                    run_id,
                    ts,
                    from_status,
                    to_status,
                    stage,
                    level,
                    event
                )
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lead_id,
                run_id,
                utcnow_iso(),
                from_status,
                to_status,
                stage,
                level,
                event,
            ),
        )

        self.conn.commit()

    def events_for_lead(
        self,
        lead_id: int,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:

        rows = self.conn.execute(
            """
            SELECT *
            FROM lead_events
            WHERE lead_id=?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                lead_id,
                limit,
            ),
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def events_for_run(
        self,
        run_id: int,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:

        rows = self.conn.execute(
            """
            SELECT *
            FROM lead_events
            WHERE run_id=?
            ORDER BY id
            LIMIT ?
            """,
            (
                run_id,
                limit,
            ),
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    # ------------------------------------------------------------------
    # KV
    # ------------------------------------------------------------------

    def kv_set(
        self,
        key: str,
        value: str,
    ) -> None:

        self.conn.execute(
            """
            INSERT INTO kv
                (key, value)
            VALUES
                (?, ?)
            ON CONFLICT(key)
            DO UPDATE SET value=excluded.value
            """,
            (
                key,
                value,
            ),
        )

        self.conn.commit()

    def kv_get(
        self,
        key: str,
    ) -> Optional[str]:

        row = self.conn.execute(
            """
            SELECT value
            FROM kv
            WHERE key=?
            """,
            (key,),
        ).fetchone()

        return (
            row["value"]
            if row
            else None
        )

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def counts_by_status(
        self,
    ) -> Dict[str, int]:

        rows = self.conn.execute(
            """
            SELECT status,
                   COUNT(*) AS n
            FROM leads
            GROUP BY status
            """
        ).fetchall()

        return {
            row["status"]: int(row["n"])
            for row in rows
        }

    def leads_for_report(
        self,
        run_id: Optional[int] = None,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:

        if run_id is not None:

            rows = self.conn.execute(
                """
                SELECT *
                FROM leads
                WHERE run_id=?
                ORDER BY id
                LIMIT ?
                """,
                (
                    run_id,
                    limit,
                ),
            ).fetchall()

        else:

            rows = self.conn.execute(
                """
                SELECT *
                FROM leads
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]