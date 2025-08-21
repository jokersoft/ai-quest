"""
See https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html
"""

import json
import logging
from dataclasses import dataclass
import uuid

import boto3
from botocore.exceptions import ClientError

from app.services.memory.i_memory_store import MemoryStoreInterface, MemorySearchResult
from app.entities.chapter import Chapter as ChapterEntity

logger = logging.getLogger(__name__)
DEFAULT_MAX_CHAPTERS = 5


@dataclass
class S3VectorConfig:
    """Configuration for S3 Vector store"""
    bucket_name: str
    bedrock_model_id: str = "amazon.titan-embed-text-v2:0"
    dimension: int = 1024  # Default dimension for v2 (can be 256, 512, or 1024)
    region: str = "eu-central-1"

@dataclass
class MemoryMetadata:
    chapter_number: int


class AWSS3MemoryStore(MemoryStoreInterface):
    """AWS S3 Vectors implementation of memory store"""

    def __init__(self, config: S3VectorConfig):
        self.config = config

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors.html
        self.s3vectors_client = boto3.client('s3vectors', region_name=config.region)
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=config.region)

    def _get_index_name(self, story_id: uuid.UUID) -> str:
        """Get index name for a specific story"""
        return f"story-{story_id}"

    def _ensure_story_index_exists(self, story_id: uuid.UUID):
        """Ensure vector index exists for the story"""
        logger.warning(f"_ensure_story_index_exists")

        index_name = self._get_index_name(story_id)

        try:
            # Check if index exists by listing indexes
            response = self.s3vectors_client.list_indexes(
                vectorBucketName=self.config.bucket_name
            )

            existing_indexes = [idx['indexName'] for idx in response.get('indexes', [])]

            if index_name in existing_indexes:
                logger.debug(f"Vector index {index_name} already exists")
                return

        except ClientError as e:
            logger.warning(f"Could not list indexes: {e}")

        # Create index for this story if it doesn't exist
        try:
            self.s3vectors_client.create_index(
                vectorBucketName=self.config.bucket_name,
                indexName=index_name,
                vectorDimension=self.config.dimension,
                distanceMetric='COSINE'
            )
            logger.info(f"Created vector index for story: {index_name}")
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                logger.error(f"Error creating index: {e}")
                raise

    async def _generate_embedding(self, text: str) -> list[float]:
        """Generate embeddings using Amazon Bedrock"""
        try:
            response = self.bedrock_client.invoke_model(
                modelId=self.config.bedrock_model_id,
                body=json.dumps({
                    "inputText": text
                })
            )

            result = json.loads(response['body'].read())
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def _format_chapter_for_embedding(self, chapter: ChapterEntity) -> str:
        """Format chapter data for embedding generation"""
        return chapter.to_json()

    async def add_memory(self, story_id: uuid.UUID, chapter: ChapterEntity) -> None:
        """Store a chapter as memory with its vector embedding"""
        # Ensure index exists for this story
        self._ensure_story_index_exists(story_id)

        # Generate embedding
        embedding_text = self._format_chapter_for_embedding(chapter)
        embedding = await self._generate_embedding(embedding_text)

        logger.warning(f"embedding: {embedding}")

        # Create object key - using story_id prefix for organization
        object_key = f"stories/{story_id}/chapter-{chapter.number}.json"

        # Add vector to the story-specific index
        try:
            self.s3vectors_client.put_object(
                Bucket=self.config.bucket_name,
                Key=object_key,
                Body=embedding,
                Metadata=MemoryMetadata(
                    chapter_number=chapter.number
                ).__dict__,
            )

            logger.info(f"Stored memory for story {story_id}, chapter {chapter.number}")

        except Exception as e:
            logger.error(f"Error storing vector: {e}")
            raise

    async def search_memories(self, story_id: uuid.UUID,
                              query: str,
                              max_results: int = 5) -> list[MemorySearchResult]:
        """Search for relevant memories using vector similarity"""
        index_name = self._get_index_name(story_id)

        logger.info(f"Searching memory for story {story_id}, query: {query}")

        # Generate query embedding
        query_embedding = await self._generate_embedding(query)

        try:
            # Query vectors in the story-specific index
            response = self.s3vectors_client.query_vectors(
                vectorBucketName=self.config.bucket_name,
                indexName=index_name,
                queryVector={"float32": query_embedding},
                topK=max_results,
                returnDistance=True,
                returnMetadata=True
            )

            results = []
            logger.info(f"response: {response}")

            vectors = response.get('vectors', [])
            for vector in vectors:
                metadata = vector.get('metadata', {})
                chapter_number = metadata.get('chapter_number', 0)
                relevance_score = vector.get('distance', 0.0)

                results.append(MemorySearchResult(
                    chapter_number=chapter_number,
                    relevance_score=relevance_score
                ))

            return results

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warning(f"No index found for story {story_id}")
                return []
            logger.error(f"Error searching memories: {e}")
            return []

    async def delete_story_memories(self, story_id: uuid.UUID) -> None:
        """Delete all memories for a story"""
        index_name = self._get_index_name(story_id)

        # First, delete the index
        try:
            self.s3vectors_client.delete_index(
                vectorBucketName=self.config.bucket_name,
                indexName=index_name
            )
            logger.info(f"Deleted vector index for story {story_id}")
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                logger.error(f"Error deleting story index: {e}")

        # Delete all objects with the story prefix
        try:
            # List all objects for this story
            response = self.s3vectors_client.list_objects_v2(
                Bucket=self.config.bucket_name,
                Prefix=f"stories/{story_id}/"
            )

            # Delete all objects
            objects_to_delete = []
            for obj in response.get('Contents', []):
                objects_to_delete.append({'Key': obj['Key']})

            if objects_to_delete:
                self.s3vectors_client.delete_objects(
                    Bucket=self.config.bucket_name,
                    Delete={'Objects': objects_to_delete}
                )

            logger.info(f"Deleted all memories for story {story_id}")
        except ClientError as e:
            logger.error(f"Error deleting story memories: {e}")
