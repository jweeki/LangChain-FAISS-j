import json
import threading
from socketserver import ThreadingMixIn
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse

from common import create_embeddings, get_storage_paths, load_vector_store, search_documents


HOST = "127.0.0.1"
PORT = 8000
DEFAULT_TOP_K = 5


class SearchService:
    def __init__(self) -> None:
        self.embeddings = None
        self.vector_store = None
        self.paths = get_storage_paths()
        self._init_lock = threading.Lock()

    def initialize(self) -> None:
        if self.vector_store is not None:
            return
        with self._init_lock:
            if self.vector_store is not None:
                return
            self.embeddings = create_embeddings()
            self.vector_store = load_vector_store(self.embeddings)

    def search(self, query: str, top_k: int) -> Dict[str, Any]:
        self.initialize()
        results = search_documents(self.vector_store, query, k=top_k)
        serialized = []
        for rank, (doc, score) in enumerate(results, start=1):
            confidence = 1 / (1 + score)
            serialized.append(
                {
                    "rank": rank,
                    "score": float(score),
                    "confidence": float(confidence),
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", ""),
                    "metadata": {k: v for k, v in doc.metadata.items() if k != "source"},
                }
            )
        return {
            "query": query,
            "top_k": top_k,
            "results": serialized,
            "paths": {k: str(v) for k, v in self.paths.items()},
        }


service = SearchService()


class SearchRequestHandler(BaseHTTPRequestHandler):
    server_version = "SearchHTTP/1.0"

    def _set_headers(self, status: int = HTTPStatus.OK, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _write_json(self, payload: Dict[str, Any], status: int = HTTPStatus.OK) -> None:
        self._set_headers(status=status)
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def _read_json(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        return json.loads(raw_body.decode("utf-8"))

    def do_OPTIONS(self) -> None:
        self._set_headers(status=HTTPStatus.NO_CONTENT)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            paths = {k: str(v) for k, v in service.paths.items()}
            self._write_json(
                {
                    "status": "ok",
                    "initialized": service.vector_store is not None,
                    "paths": paths,
                }
            )
            return

        self._write_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/search":
            self._write_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return

        try:
            payload = self._read_json()
            query = str(payload.get("query", "")).strip()
            top_k = int(payload.get("topK", DEFAULT_TOP_K))
            if not query:
                self._write_json({"error": "query 不能为空"}, status=HTTPStatus.BAD_REQUEST)
                return
            if top_k < 1:
                self._write_json({"error": "topK 必须大于 0"}, status=HTTPStatus.BAD_REQUEST)
                return

            response = service.search(query=query, top_k=top_k)
            self._write_json(response)
        except FileNotFoundError as exc:
            self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            self._write_json({"error": f"{type(exc).__name__}: {exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def log_message(self, format: str, *args) -> None:
        return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def main() -> None:
    paths = service.paths
    print(f"Model dir: {Path(paths['model_dir'])}")
    print(f"Vector store dir: {Path(paths['vector_store_dir'])}")
    print("Preloading embeddings model and vector store...")
    service.initialize()
    print("Preload completed.")

    server = ThreadedHTTPServer((HOST, PORT), SearchRequestHandler)
    print(f"Search API started: http://{HOST}:{PORT}")
    print("Endpoints: GET /api/health, POST /api/search")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
