from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer

from src.config import settings


class VectorStore:
    def __init__(self) -> None:
        self._client: QdrantClient | None = None
        self._host = settings.qdrant_host
        self._port = settings.qdrant_port
        self._grpc_port = settings.qdrant_grpc_port
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

    @property
    def client(self) -> QdrantClient:
        if self._client is None:
            self._client = QdrantClient(
                host=self._host,
                port=self._port,
                grpc_port=self._grpc_port,
            )
            self._ensure_collection()
        return self._client

    def _ensure_collection(self) -> None:
        collections = self.client.get_collections().collections
        names = {c.name for c in collections}
        if settings.collection_name not in names:
            vector_size = self.encoder.get_sentence_embedding_dimension()
            if vector_size is None:
                msg = "Failed to determine embedding dimension"
                raise ValueError(msg)
            self.client.create_collection(
                collection_name=settings.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def ingest(self, documents: list[dict[str, str]]) -> None:
        if not documents:
            return
        texts = [d["content"] for d in documents]
        vectors = self.encoder.encode(texts).tolist()
        points = [
            {
                "id": i,
                "vector": vec,
                "payload": {"title": doc["title"], "content": doc["content"], "tags": doc.get("tags", [])},
            }
            for i, (vec, doc) in enumerate(zip(vectors, documents, strict=False))
        ]
        self.client.upsert(collection_name=settings.collection_name, points=points)  # type: ignore[arg-type]

    def search(self, query: str, top_k: int = 3) -> list[dict[str, str]]:
        vector = self.encoder.encode(query).tolist()
        results = self.client.search(  # type: ignore[attr-defined]
            collection_name=settings.collection_name,
            query_vector=vector,
            limit=top_k,
        )
        return [r.payload for r in results if r.payload]
