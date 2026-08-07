import json
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.core.constants import EMBEDDINGS_DIR
from app.core.logger import get_logger
from app.services.embedding_service import EmbeddingService

logger = get_logger(__name__)

INDEX_PATH = EMBEDDINGS_DIR / "vector_index.json"

try:  # pragma: no cover - optional dependency
    from pinecone import Pinecone

    _PINECONE_AVAILABLE = True
except Exception:  # noqa: BLE001  # any package failure must degrade gracefully
    _PINECONE_AVAILABLE = False


class VectorService:
    """Vector store facade.

    Uses Pinecone when configured (``VECTOR_STORE=pinecone`` + ``PINECONE_API_KEY``)
    and otherwise falls back to a local JSON-backed index, keeping the application
    fully functional without external services.
    """

    def __init__(self, index_path: str | Path | None = None) -> None:
        self.index_path = Path(index_path) if index_path else INDEX_PATH
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.embedding_service = EmbeddingService()
        self._pinecone = None
        self.load_index()

    # -- local index persistence -------------------------------------------------

    def load_index(self) -> None:
        if self.index_path.exists():
            try:
                with self.index_path.open("r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = []
        else:
            self.data = []

    def save_index(self) -> None:
        try:
            with self.index_path.open("w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception:  # noqa: S110  # persistence is best-effort; in-memory index stays valid
            pass

    # -- Pinecone integration ----------------------------------------------------

    def _get_pinecone(self) -> Any | None:
        if not settings.use_pinecone or not _PINECONE_AVAILABLE:
            return None
        if self._pinecone is None:
            try:
                client = Pinecone(api_key=settings.pinecone_api_key)
                if settings.pinecone_index_name not in client.list_indexes().names():
                    client.create_index(
                        name=settings.pinecone_index_name,
                        dimension=self.embedding_service.dimension,
                        spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
                    )
                self._pinecone = client.Index(settings.pinecone_index_name)
                logger.info("Connected to Pinecone index '%s'", settings.pinecone_index_name)
            except Exception as exc:  # noqa: BLE001  # graceful fallback
                logger.warning("Pinecone unavailable (%s); using local vector index", exc)
                self._pinecone = None
        return self._pinecone

    # -- public API ---------------------------------------------------------------

    def upsert_vectors(self, items: list[dict[str, Any]]) -> None:
        """Upsert a list of ``{id, vector, text, metadata}`` dicts."""
        pinecone = self._get_pinecone()
        if pinecone is not None:
            try:
                vectors = [
                    {
                        "id": item["id"],
                        "values": item.get("vector") or self.embedding_service.embed_text(item["text"]),
                        "metadata": item.get("metadata", {}),
                    }
                    for item in items
                ]
                pinecone.upsert(vectors=vectors)
                return
            except Exception as exc:  # noqa: BLE001  # graceful fallback
                logger.warning("Pinecone upsert failed (%s); writing to local index", exc)

        ids_to_add = {item["id"] for item in items}
        self.data = [d for d in self.data if d["id"] not in ids_to_add]
        for item in items:
            self.data.append(
                {
                    "id": item["id"],
                    "vector": item.get("vector") or self.embedding_service.embed_text(item["text"]),
                    "text": item["text"],
                    "metadata": item.get("metadata", {}),
                }
            )
        self.save_index()

    def query_vectors(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        pinecone = self._get_pinecone()
        if pinecone is not None:
            try:
                query_vector = self.embedding_service.embed_text(query)
                response = pinecone.query(vector=query_vector, top_k=top_k, include_metadata=True)
                results = []
                for match in response.get("matches", []):
                    metadata = match.get("metadata", {}) or {}
                    results.append(
                        {
                            "id": match.get("id", ""),
                            "text": metadata.get("text", ""),
                            "metadata": metadata,
                            "score": match.get("score", 0.0),
                        }
                    )
                return results
            except Exception as exc:  # noqa: BLE001  # graceful fallback
                logger.warning("Pinecone query failed (%s); querying local index", exc)

        if not self.data:
            return []

        query_words = set(query.lower().split())
        results = []
        for entry in self.data:
            text = entry["text"].lower()
            score = 0.0
            overlap = 0
            for word in query_words:
                if word in text:
                    overlap += 1
            if query_words:
                score += (overlap / len(query_words)) * 10.0
            results.append((entry, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return [
            {"id": r[0]["id"], "text": r[0]["text"], "metadata": r[0]["metadata"], "score": r[1]}
            for r in results[:top_k]
            if r[1] > 0
        ]
