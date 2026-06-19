import hashlib
import random
import logging

logger = logging.getLogger("metaai.rag")


class DocumentProcessor:
    def __init__(self, chunk_size: int = 512, overlap: int = 64):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_by_fixed_size(self, text: str) -> list[dict]:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]
            chunk_id = hashlib.md5(chunk_text.encode(), usedforsecurity=False).hexdigest()[:12]
            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "start_pos": start,
                "end_pos": end,
                "chunk_index": len(chunks),
            })
            start += self.chunk_size - self.overlap
        return chunks

    def chunk_by_paragraph(self, text: str) -> list[dict]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        for i, para in enumerate(paragraphs):
            if len(para) > self.chunk_size:
                sub_chunks = self.chunk_by_fixed_size(para)
                chunks.extend(sub_chunks)
            else:
                chunk_id = hashlib.md5(para.encode(), usedforsecurity=False).hexdigest()[:12]
                chunks.append({
                    "id": chunk_id,
                    "text": para,
                    "start_pos": sum(len(p) + 2 for p in paragraphs[:i]),
                    "end_pos": sum(len(p) + 2 for p in paragraphs[:i + 1]),
                    "chunk_index": len(chunks),
                })
        return chunks

    def chunk_by_sentence(self, text: str) -> list[dict]:
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        current = ""
        chunks = []
        for sent in sentences:
            if len(current) + len(sent) > self.chunk_size and current:
                chunk_id = hashlib.md5(current.encode(), usedforsecurity=False).hexdigest()[:12]
                chunks.append({
                    "id": chunk_id,
                    "text": current,
                    "chunk_index": len(chunks),
                })
                current = sent
            else:
                current += (" " + sent) if current else sent
        if current:
            chunk_id = hashlib.md5(current.encode(), usedforsecurity=False).hexdigest()[:12]
            chunks.append({
                "id": chunk_id,
                "text": current,
                "chunk_index": len(chunks),
            })
        return chunks

    def process(self, text: str, strategy: str = "fixed") -> list[dict]:
        if strategy == "paragraph":
            return self.chunk_by_paragraph(text)
        elif strategy == "sentence":
            return self.chunk_by_sentence(text)
        return self.chunk_by_fixed_size(text)


class EmbeddingService:
    def __init__(self, model: str = "BAAI/bge-base-en-v1.5"):
        self.model = model

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        dim = 768 if "bge" in self.model else 1536
        return [
            [random.uniform(-0.05, 0.05) for _ in range(dim)]
            for _ in texts
        ]

    async def embed_query(self, query: str) -> list[float]:
        dim = 768 if "bge" in self.model else 1536
        return [random.uniform(-0.05, 0.05) for _ in range(dim)]


class RetrievalService:
    def __init__(self):
        self.embedder = EmbeddingService()

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        strategy: str = "hybrid",
        rerank: bool = True,
    ) -> list[dict]:
        query_embedding = await self.embedder.embed_query(query)

        if strategy == "dense":
            results = self._dense_search(query_embedding, top_k)
        elif strategy == "sparse":
            results = self._sparse_search(query, top_k)
        else:
            dense = self._dense_search(query_embedding, top_k)
            sparse = self._sparse_search(query, top_k)
            results = self._hybrid_fusion(dense, sparse, top_k)

        if rerank and results:
            results = self._rerank(query, results)

        return results

    def _dense_search(self, query_embedding: list[float], top_k: int) -> list[dict]:
        return [
            {
                "chunk_id": f"chunk_{i}",
                "text": f"Financial document content chunk {i} about market trends and portfolio allocation.",
                "score": round(0.95 - (i * 0.05), 4),
                "source": f"doc_{random.randint(1, 10)}",
                "metadata": {"page": random.randint(1, 50), "section": "analysis"},
            }
            for i in range(top_k)
        ]

    def _sparse_search(self, query: str, top_k: int) -> list[dict]:
        return [
            {
                "chunk_id": f"sparse_{i}",
                "text": f"Document matching keywords: {query[:50]} - section {i}.",
                "score": round(0.8 - (i * 0.06), 4),
                "source": f"doc_{random.randint(1, 10)}",
                "metadata": {"page": random.randint(1, 50), "section": "keywords"},
            }
            for i in range(top_k)
        ]

    def _hybrid_fusion(self, dense: list[dict], sparse: list[dict], top_k: int) -> list[dict]:
        seen = set()
        fused = []
        for d, s in zip(dense, sparse):
            if d["chunk_id"] not in seen:
                d["score"] = round(d["score"] * 0.6 + 0.1, 4)
                fused.append(d)
                seen.add(d["chunk_id"])
            if s["chunk_id"] not in seen and len(fused) < top_k:
                s["score"] = round(s["score"] * 0.4 + 0.1, 4)
                fused.append(s)
                seen.add(s["chunk_id"])
        fused.sort(key=lambda x: x["score"], reverse=True)
        return fused[:top_k]

    def _rerank(self, query: str, results: list[dict]) -> list[dict]:
        for r in results:
            r["rerank_score"] = round(r["score"] * random.uniform(0.9, 1.1), 4)
        results.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
        for i, r in enumerate(results):
            r["rank"] = i + 1
        return results


class RerankingService:
    def __init__(self, model: str = "BAAI/bge-reranker-v2-m3"):
        self.model = model

    async def rerank(self, query: str, documents: list[dict], top_k: int = 5) -> list[dict]:
        scored = []
        for doc in documents:
            relevance = random.uniform(0.3, 0.99)
            scored.append({**doc, "rerank_score": round(relevance, 4)})
        scored.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored[:top_k]


class CitationGenerator:
    def __init__(self):
        self.citation_counter = 0

    def generate_citations(self, query: str, retrieved_chunks: list[dict]) -> list[dict]:
        citations = []
        for chunk in retrieved_chunks:
            self.citation_counter += 1
            citations.append({
                "citation_id": f"[{self.citation_counter}]",
                "source": chunk.get("source", "unknown"),
                "text_snippet": chunk.get("text", "")[:200],
                "relevance_score": chunk.get("score", 0),
                "metadata": chunk.get("metadata", {}),
            })
        return citations

    def format_cited_response(self, response: str, citations: list[dict]) -> str:
        if not citations:
            return response
        citation_marks = " ".join(c["citation_id"] for c in citations)
        return f"{response}\n\nSources: {citation_marks}"
