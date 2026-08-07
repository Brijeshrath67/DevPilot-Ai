import json
from pathlib import Path
from typing import Any

INDEX_PATH = Path(__file__).resolve().parents[2] / "data" / "embeddings" / "vector_index.json"


class VectorService:
    def __init__(self, index_path: str | Path | None = None) -> None:
        self.index_path = Path(index_path) if index_path else INDEX_PATH
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.load_index()

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

    def upsert_vectors(self, items: list[dict[str, Any]]) -> None:
        """
        Expects a list of dicts:
        {
          "id": str,
          "vector": List[float],
          "text": str,
          "metadata": Dict[str, Any]
        }
        """
        # Remove duplicates
        ids_to_add = {item["id"] for item in items}
        self.data = [d for d in self.data if d["id"] not in ids_to_add]

        for item in items:
            self.data.append(
                {"id": item["id"], "vector": item["vector"], "text": item["text"], "metadata": item.get("metadata", {})}
            )
        self.save_index()

    def query_vectors(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        if not self.data:
            return []

        # We can do keyword/token matching fallback in case we do not have real embeddings
        # Let's clean the query
        query_words = set(query.lower().split())

        results = []
        for entry in self.data:
            text = entry["text"].lower()
            score = 0.0

            # Simple TF-IDF approximation based on token overlap
            overlap = 0
            for word in query_words:
                if word in text:
                    overlap += 1

            if len(query_words) > 0:
                score += (overlap / len(query_words)) * 10.0

            results.append((entry, score))

        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)

        # Format response
        return [
            {"id": r[0]["id"], "text": r[0]["text"], "metadata": r[0]["metadata"], "score": r[1]}
            for r in results[:top_k]
            if r[1] > 0
        ]
