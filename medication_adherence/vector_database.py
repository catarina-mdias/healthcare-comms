import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from langchain_chroma import Chroma
from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings


@dataclass
class SimilaritySearchResult:
    document_id: int
    content: str
    similarity_score: float


class VectorDatabase:
    def __init__(
        self,
        kb_file_name: str,
        kb_directory_path: Path,
        embedding_model: str,
        openai_key: str,
        file_jq_schema: str,
    ):
        self.kb_directory_path = kb_directory_path
        self.kb_file_name = kb_file_name

        self._validate_schema(file_jq_schema)
        self.file_jq_schema = file_jq_schema

        logging.info("Initializing VectorDatabase.")

        # Load from documents
        documents = self._load_documents(
            jq_schema=file_jq_schema,
        )

        logging.info(f"Loaded {len(documents)} documents.")

        self._store = self._get_store_from_documents(
            documents=documents,
            embedding_model=embedding_model,
            openai_key=openai_key,
        )
        logging.info("Initialized VectorDatabase from documents.")

    def _get_store_from_documents(
        self, documents: List[Document], embedding_model: str, openai_key: str
    ) -> Chroma:
        emb_func = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=openai_key,
        )

        return Chroma.from_documents(
            collection_name=self.kb_file_name,
            documents=documents,
            embedding=emb_func,
            collection_metadata={"hnsw:space": "cosine"},
        )

    def _validate_schema(self, schema: str):
        """
        Validate that the schema follows the expected format with content
        and metadata.id
        """
        if (
            not schema
            or "{content:" not in schema
            or "metadata: {id:" not in schema
        ):
            raise ValueError(
                "Schema must include 'content' and 'metadata.id'."
            )

    def get_documents_with_similarity_score(
        self,
        user_query: str,
        top_k: int,
        score_threshold: float,
        retrieval_filter: Optional[Dict] = None,
    ) -> List[SimilaritySearchResult]:
        logging.info(f"Getting documents for user query: {user_query}.")

        retrieved_docs = self._store.similarity_search_with_relevance_scores(
            query=user_query,
            k=top_k,
            score_threshold=score_threshold,
            filter=retrieval_filter,
        )

        logging.info(f"Retrieved {len(retrieved_docs)} documents.")

        similar_docs = []
        for doc, score in retrieved_docs:
            doc_content = json.loads(doc.page_content)
            similar_docs.append(
                SimilaritySearchResult(
                    document_id=doc_content["metadata"]["id"],
                    content=doc_content["content"],
                    similarity_score=score,
                )
            )

        return similar_docs

    def close(self):
        self._store.delete_collection()

    def _load_documents(
        self,
        jq_schema: str,
    ) -> List[Document]:
        kb_path = Path(self.kb_directory_path, self.kb_file_name)

        logging.info(f"Loading articles from {kb_path}.")

        loader = JSONLoader(
            file_path=kb_path,
            jq_schema=jq_schema,
            text_content=False,
        )

        return loader.load()
