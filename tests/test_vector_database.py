import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from communication.vector_database import (
    SimilaritySearchResult,
    VectorDatabase,
)


class TestVectorDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.kb_directory_path = Path(self.temp_dir.name)
        self.kb_file_name = "test_kb.json"

        test_data = [
            {"content": "This is test document 1", "metadata": {"id": 1}},
            {"content": "This is test document 2", "metadata": {"id": 2}},
        ]

        with open(
            os.path.join(self.kb_directory_path, self.kb_file_name), "w"
        ) as f:
            json.dump(test_data, f)

        self.embedding_model = "text-embedding-3-small"
        self.openai_key = "test-key"
        self.file_jq_schema = (
            ".[] | {content: .content, metadata: {id: .metadata.id}}"
        )

        self.mock_chroma_patcher = patch(
            "communication.vector_database.Chroma"
        )
        self.mock_chroma = self.mock_chroma_patcher.start()

        self.mock_embeddings_patcher = patch(
            "communication.vector_database.OpenAIEmbeddings"
        )
        self.mock_embeddings = self.mock_embeddings_patcher.start()

        self.mock_json_loader_patcher = patch(
            "communication.vector_database.JSONLoader"
        )
        self.mock_json_loader = self.mock_json_loader_patcher.start()

        self.mock_documents = [
            MagicMock(
                page_content=json.dumps(
                    {
                        "content": "This is test document 1",
                        "metadata": {"id": 1},
                    }
                )
            ),
            MagicMock(
                page_content=json.dumps(
                    {
                        "content": "This is test document 2",
                        "metadata": {"id": 2},
                    }
                )
            ),
        ]

        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = self.mock_documents
        self.mock_json_loader.return_value = mock_loader_instance

        self.mock_store = MagicMock()
        self.mock_chroma.from_documents.return_value = self.mock_store

    def tearDown(self):
        self.temp_dir.cleanup()
        self.mock_chroma_patcher.stop()
        self.mock_embeddings_patcher.stop()
        self.mock_json_loader_patcher.stop()

    def test_init(self):
        """Test proper initialization of the VectorDatabase class"""
        _ = VectorDatabase(
            kb_file_name=self.kb_file_name,
            kb_directory_path=self.kb_directory_path,
            embedding_model=self.embedding_model,
            openai_key=self.openai_key,
            file_jq_schema=self.file_jq_schema,
        )

        # Verify JSON loader was called with correct parameters
        self.mock_json_loader.assert_called_once_with(
            file_path=Path(self.kb_directory_path, self.kb_file_name),
            jq_schema=self.file_jq_schema,
            text_content=False,
        )

        # Verify embeddings were initialized with correct parameters
        self.mock_embeddings.assert_called_once_with(
            model=self.embedding_model,
            openai_api_key=self.openai_key,
        )

        # Verify Chroma was initialized with correct parameters
        self.mock_chroma.from_documents.assert_called_once()
        call_args = self.mock_chroma.from_documents.call_args[1]
        self.assertEqual(call_args["collection_name"], self.kb_file_name)
        self.assertEqual(call_args["documents"], self.mock_documents)
        self.assertEqual(
            call_args["collection_metadata"], {"hnsw:space": "cosine"}
        )

    def test_validate_schema_valid(self):
        """Test schema validation with valid schema"""
        db = VectorDatabase(
            kb_file_name=self.kb_file_name,
            kb_directory_path=self.kb_directory_path,
            embedding_model=self.embedding_model,
            openai_key=self.openai_key,
            file_jq_schema=self.file_jq_schema,
        )

        db._validate_schema(self.file_jq_schema)

    def test_validate_schema_invalid(self):
        """Test schema validation with invalid schema"""
        with self.assertRaises(ValueError):
            _ = VectorDatabase(
                kb_file_name=self.kb_file_name,
                kb_directory_path=self.kb_directory_path,
                embedding_model=self.embedding_model,
                openai_key=self.openai_key,
                file_jq_schema=".[] | {text: .content}",
            )

    def test_get_documents_with_similarity_score(self):
        """Test retrieving documents with similarity scores"""
        db = VectorDatabase(
            kb_file_name=self.kb_file_name,
            kb_directory_path=self.kb_directory_path,
            embedding_model=self.embedding_model,
            openai_key=self.openai_key,
            file_jq_schema=self.file_jq_schema,
        )

        mock_results = [
            (self.mock_documents[0], 0.92),
            (self.mock_documents[1], 0.85),
        ]
        self.mock_store.similarity_search_with_relevance_scores.return_value = (  # noqa
            mock_results
        )

        # Test similarity score method
        results = db.get_documents_with_similarity_score(
            user_query="test query",
            top_k=2,
            score_threshold=0.8,
            retrieval_filter={"metadata": {"key": "value"}},
        )

        # Verify the store method was called with correct parameters
        self.mock_store.similarity_search_with_relevance_scores.assert_called_once_with(  # noqa
            query="test query",
            k=2,
            score_threshold=0.8,
            filter={"metadata": {"key": "value"}},
        )

        # Verify returned results are correct
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], SimilaritySearchResult)
        self.assertEqual(results[0].document_id, 1)
        self.assertEqual(results[0].content, "This is test document 1")
        self.assertEqual(results[0].similarity_score, 0.92)
        self.assertEqual(results[1].document_id, 2)
        self.assertEqual(results[1].content, "This is test document 2")
        self.assertEqual(results[1].similarity_score, 0.85)
