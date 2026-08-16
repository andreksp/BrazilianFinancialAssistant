"""
ChromaDB client for semantic search over Brazilian financial regulations.
Loaded once on startup; provides context for LLM responses (RAG pattern).
"""

import hashlib
import logging
from pathlib import Path
from typing import List, Optional

import chromadb

from app.core.config import settings

logger = logging.getLogger(__name__)

# Map filename prefixes to asset-type collections
_ASSET_TYPE_MAP = {
    "ir_acoes": "acoes",
    "ir_bdrs": "acoes",   # BDRs follow same rules as stocks
    "ir_fiis": "geral",
    "ir_opcoes": "acoes",
    "b3_fees": "geral",
    "darf_guide": "geral",
}


class ChromaDBClient:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.collection_geral = self.client.get_or_create_collection(
            name="regulacoes_geral",
            metadata={"description": "General regulations (IR, DARF, fees)"},
        )
        self.collection_acoes = self.client.get_or_create_collection(
            name="regulacoes_acoes",
            metadata={"description": "Regulations for stocks, BDRs, and options"},
        )

    def _collection_for(self, asset_type: str):
        return self.collection_acoes if asset_type == "acoes" else self.collection_geral

    def add_regulation(
        self,
        doc_id: str,
        title: str,
        content: str,
        asset_type: str = "geral",
    ) -> None:
        collection = self._collection_for(asset_type)
        collection.upsert(
            documents=[content],
            metadatas=[{"title": title, "asset_type": asset_type}],
            ids=[doc_id],
        )
        logger.debug(f"Upserted regulation '{title}' into '{asset_type}' collection")

    def search_regulations(
        self,
        query: str,
        asset_type: str = "geral",
        top_k: int = 3,
    ) -> List[str]:
        """
        Semantic search over regulations. Searches the asset-specific collection
        first; falls back to the general collection if fewer than top_k results.
        """
        results: List[str] = []

        if asset_type == "acoes":
            try:
                count = self.collection_acoes.count()
                if count > 0:
                    r = self.collection_acoes.query(
                        query_texts=[query],
                        n_results=min(top_k, count),
                    )
                    if r and r["documents"]:
                        results.extend(r["documents"][0])
            except Exception as e:
                logger.warning(f"ChromaDB acoes query failed: {e}")

        try:
            count = self.collection_geral.count()
            remaining = top_k - len(results)
            if count > 0 and remaining > 0:
                r = self.collection_geral.query(
                    query_texts=[query],
                    n_results=min(remaining, count),
                )
                if r and r["documents"]:
                    results.extend(r["documents"][0])
        except Exception as e:
            logger.warning(f"ChromaDB geral query failed: {e}")

        return results

    def load_initial_regulations(self) -> None:
        """
        Load regulation .txt files from /backend/data/regulations/ into ChromaDB.
        Uses upsert so re-running on restart is idempotent.
        """
        regulations_dir = Path(__file__).parent.parent.parent / "data" / "regulations"
        if not regulations_dir.exists():
            logger.warning(f"Regulations directory not found: {regulations_dir}")
            return

        loaded = 0
        for txt_file in sorted(regulations_dir.glob("*.txt")):
            try:
                content = txt_file.read_text(encoding="utf-8")
                title = txt_file.stem.replace("_", " ").title()
                asset_type = _ASSET_TYPE_MAP.get(txt_file.stem, "geral")

                # Stable ID = hash of filename (avoids duplicates on restart)
                doc_id = hashlib.md5(txt_file.name.encode()).hexdigest()

                self.add_regulation(doc_id, title, content, asset_type)
                loaded += 1
                logger.info(f"Loaded regulation: {txt_file.name} → {asset_type}")
            except Exception as e:
                logger.error(f"Failed to load {txt_file.name}: {e}")

        logger.info(f"ChromaDB: {loaded} regulation(s) loaded.")


_client: Optional[ChromaDBClient] = None


def get_chroma_client() -> Optional[ChromaDBClient]:
    """Return shared ChromaDB client, or None if initialization fails."""
    global _client
    if _client is None:
        try:
            _client = ChromaDBClient()
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            return None
    return _client
