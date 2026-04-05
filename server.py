from __future__ import annotations

import json
import sqlite3
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "progress.db"
VALID_STATUSES = {"known", "fuzzy", "unknown"}


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS word_statuses (
                word TEXT PRIMARY KEY,
                status TEXT NOT NULL CHECK(status IN ('known', 'fuzzy', 'unknown')),
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def load_statuses() -> dict[str, str]:
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("SELECT word, status FROM word_statuses").fetchall()
    return {word: status for word, status in rows}


def upsert_status(word: str, status: str) -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO word_statuses(word, status, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(word) DO UPDATE SET
                status = excluded.status,
                updated_at = CURRENT_TIMESTAMP
            """,
            (word, status),
        )
        connection.commit()


class AppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/statuses":
            self._send_json({"statuses": load_statuses()})
            return
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/statuses":
            self._handle_save_status()
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Unknown API endpoint.")

    def _handle_save_status(self) -> None:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Request body must be valid JSON.")
            return

        word = str(payload.get("word", "")).strip()
        status = str(payload.get("status", "")).strip()

        if not word:
            self.send_error(HTTPStatus.BAD_REQUEST, "Field 'word' is required.")
            return
        if status not in VALID_STATUSES:
            self.send_error(
                HTTPStatus.BAD_REQUEST,
                "Field 'status' must be one of: known, fuzzy, unknown.",
            )
            return

        upsert_status(word, status)
        self._send_json({"ok": True, "word": word, "status": status})

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        super().log_message(format, *args)


def main() -> None:
    init_db()
    host = "0.0.0.0"
    port = 8000
    server = ThreadingHTTPServer((host, port), AppHandler)
    print(f"Serving on http://{host}:{port}")
    print("Accessible from your LAN via this machine's local IP, for example:")
    print(f"  http://<your-local-ip>:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
