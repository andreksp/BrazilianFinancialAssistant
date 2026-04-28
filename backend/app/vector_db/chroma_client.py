"""
ChromaDB client for semantic search of regulations (Phase 3).

Reference: Documentation/research.md for tax rules and regulations
Purpose: Store embeddings of Brazilian financial regulations for RAG

Features:
- Semantic search: Find relevant regulations by keyword/question
- Scoped by asset type (Phase 7 multi-agent)
- Persistent storage in local SQLite
"""

import logging
from typing import List, Optional

import chromadb

from app.core.config import settings

logger = logging.getLogger(__name__)


class ChromaDBClient:
    """Client for managing vector embeddings of regulations."""

    def __init__(self):
        """Initialize ChromaDB client."""
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)

        # Create collections for each asset type
        self.collection_geral = self.client.get_or_create_collection(
            name="regulacoes_geral",
            metadata={"description": "General regulations (IR, DARF, etc)"},
        )

        self.collection_acoes = self.client.get_or_create_collection(
            name="regulacoes_acoes",
            metadata={"description": "Regulations specific to stocks"},
        )

        self.collection_derivativos = self.client.get_or_create_collection(
            name="regulacoes_derivativos",
            metadata={"description": "Regulations for futures/derivatives"},
        )

    def add_regulation(
        self,
        title: str,
        content: str,
        asset_type: str = "geral",
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Add a regulation document to ChromaDB.

        Args:
            title: Regulation title
            content: Full regulation text
            asset_type: Which collection to add to (geral, acoes, derivativos)
            metadata: Optional metadata dict

        Returns:
            Document ID
        """
        if not metadata:
            metadata = {}

        metadata["title"] = title
        metadata["asset_type"] = asset_type

        # Get appropriate collection
        if asset_type == "acoes":
            collection = self.collection_acoes
        elif asset_type == "derivativos":
            collection = self.collection_derivativos
        else:
            collection = self.collection_geral

        # Add to collection
        doc_id = f"{asset_type}_{len(title)}"  # Simple ID generation
        collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id],
        )

        logger.info(f"Added regulation: {title}")
        return doc_id

    def search_regulations(
        self,
        query: str,
        asset_type: str = "geral",
        top_k: int = 5,
    ) -> List[str]:
        """
        Search regulations using semantic similarity.

        Args:
            query: Search query in Portuguese
            asset_type: Collection to search (geral, acoes, derivativos)
            top_k: Number of results to return

        Returns:
            List of relevant regulation excerpts
        """
        # Select collection
        if asset_type == "acoes":
            collection = self.collection_acoes
        elif asset_type == "derivativos":
            collection = self.collection_derivativos
        else:
            collection = self.collection_geral

        # Search
        results = collection.query(
            query_texts=[query],
            n_results=top_k,
        )

        if results and results["documents"]:
            return results["documents"][0]
        return []

    def load_initial_regulations(self) -> None:
        """
        Load initial regulations from /backend/data/regulations/ directory.

        Phase 3: Called on application startup.
        """
        # TODO: Implement loading from files
        # Read files from /backend/data/regulations/
        # Split by asset type
        # Add to appropriate collections
        logger.info("Loading initial regulations into ChromaDB...")
        pass


# Module-level client instance
_client: Optional[ChromaDBClient] = None


def get_chroma_client() -> ChromaDBClient:
    """Get or create global ChromaDB client instance."""
    global _client
    if _client is None:
        _client = ChromaDBClient()
    return _client
