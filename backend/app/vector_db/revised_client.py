"""Experimental versioned chunks with globally ranked cosine retrieval."""
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from app.core.config import settings
from app.vector_db.curated import DOCUMENTS

class ChromaDBClient:
    def __init__(self):
        self.client=chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.collection=self.client.get_or_create_collection(name='regulacoes_revisadas_v1',
            embedding_function=DefaultEmbeddingFunction(), metadata={'hnsw:space':'cosine'})
    def load_initial_regulations(self):
        self.collection.upsert(ids=[d['id'] for d in DOCUMENTS],documents=[d['text'] for d in DOCUMENTS],
            metadatas=[{k:v for k,v in d.items() if k not in ('id','text')} for d in DOCUMENTS])
    def search_evidence(self,query,top_k=3):
        if top_k<1 or not self.collection.count(): return []
        r=self.collection.query(query_texts=[query],n_results=min(top_k,self.collection.count()))
        return [dict(id=i,text=t,metadata=m,distance=float(d)) for i,t,m,d in
                zip(r['ids'][0],r['documents'][0],r['metadatas'][0],r['distances'][0])]
    def search_regulations(self,query,asset_type='geral',top_k=3):
        return [f"[{d['id']}] Fonte: {d['metadata']['source']}\nConsulta: {d['metadata']['checked_at']}\n{d['text']}"
                for d in self.search_evidence(query,top_k)]

_client=None
def get_chroma_client():
    global _client
    if _client is None: _client=ChromaDBClient()
    return _client
