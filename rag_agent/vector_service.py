import os
import json
import logging
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder
from redis import Redis
import functools
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        # 1. Environment & Connection Setup
        self.mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
        self.db_name = os.getenv("DB_NAME", "aligned_db")
        self.collection_name = os.getenv("COLLECTION_NAME", "esg_data")
        self.index_name = "vector_index"
        
        if not self.mongo_uri:
            logger.warning("MONGO_URI or MONGODB_URI not set. Vector search will fail.")

        # Redis Cache
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        try:
            self.redis_client = Redis(host=redis_host, port=redis_port, db=0)
            self.redis_client.ping() # Check connection
            logger.info("Connected to Redis.")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None

        # 2. Embedding Model (BGE-Large)
        logger.info("Loading BGE-Large embeddings...")
        self.embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")

        # 3. Cross-Encoder for Re-ranking
        logger.info("Loading Cross-Encoder...")
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

        # 4. MongoDB Client
        try:
            self.client = MongoClient(self.mongo_uri)
            self.collection = self.client[self.db_name][self.collection_name]
            self.vector_store = MongoDBAtlasVectorSearch(
                collection=self.collection,
                embedding=self.embeddings,
                index_name=self.index_name
            )
            logger.info("Connected to MongoDB Atlas.")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.vector_store = None

    def _get_cache_key(self, query: str, filters: Dict) -> str:
        """Generate a unique cache key based on query and filters."""
        filter_str = json.dumps(filters, sort_keys=True)
        return f"vector_search:{query}:{filter_str}"

    def create_index(self):
        """
        Creates the Atlas Vector Search index if it doesn't exist.
        """
        if self.collection is None:
            logger.warning("No collection connection.")
            return

        index_name = self.index_name
        model = {
            "definition": {
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": 1024,
                        "similarity": "cosine"
                    },
                    {
                        "type": "filter",
                        "path": "industry"
                    },
                    {
                        "type": "filter",
                        "path": "region"
                    },
                    {
                        "type": "filter",
                        "path": "esg_score_category"
                    }
                ]
            }
        }
        
        try:
            # Check existing indexes (if driver supports list_search_indexes which varies)
            # Simplest way: try to create. If exists, it might error or succeed idly.
            # search_indexes = list(self.collection.list_search_indexes()) # might be empty
            logger.info(f"Attempting to create search index: {index_name}")
            self.collection.create_search_index(model=model, name=index_name, type="vectorSearch")
            logger.info("Index creation command sent. It may take a minute to become active.")
        except Exception as e:
            logger.error(f"Failed to create index (might already exist or permission error): {e}")

    def rerank_results(self, query: str, documents: List[Dict], top_n: int = 5) -> List[Dict]:
        """
        Re-ranks results based on:
        Score = (Relevance * 0.4) + (ESG_Impact * 0.4) + (ROI_Potential * 0.2)
        """
        if not documents:
            return []

        # 1. Calculate Semantic Relevance (Cross-Encoder)
        doc_texts = [doc.get('page_content', '') or doc.get('text', '') for doc in documents]
        pairs = [[query, text] for text in doc_texts]
        
        # Predict returns a list of float scores (usually unbounded logits or 0-1 depending on model)
        # MS-MARCO models usually output logits. sigmoid can be applied but relative order matters.
        relevance_scores = self.cross_encoder.predict(pairs)

        # Normalize relevance scores to 0-1 range for the formula (simple min-max normalization for this batch)
        if len(relevance_scores) > 0:
            min_score = min(relevance_scores)
            max_score = max(relevance_scores)
            if max_score != min_score:
                norm_relevance = [(s - min_score) / (max_score - min_score) for s in relevance_scores]
            else:
                norm_relevance = [1.0] * len(relevance_scores)
        else:
            norm_relevance = []

        reranked_docs = []
        for i, doc in enumerate(documents):
            # Extract metadata with defaults
            metadata = doc.get('metadata', {})
            esg_impact = metadata.get('esg_impact', 0.5)
            roi_potential = metadata.get('roi_potential', 0.5)
            relevance = norm_relevance[i]

            # 2. Optimization Formula
            # Score = (Relevance * 0.4) + (ESG_Impact * 0.4) + (ROI_Potential * 0.2)
            final_score = (relevance * 0.4) + (esg_impact * 0.4) + (roi_potential * 0.2)

            doc['combined_score'] = final_score
            doc['relevance_score'] = relevance # Keep track of raw relevance
            reranked_docs.append(doc)

        # Sort by final score descending
        reranked_docs = sorted(reranked_docs, key=lambda x: x['combined_score'], reverse=True)
        return reranked_docs[:top_n]

    def search_projects(self, query: str, filters: Dict[str, Any] = None, top_k: int = 20, top_n: int = 3) -> List[Dict]:
        """
        Full pipeline: Check Cache -> Pre-Filter -> Vector Search -> Re-Rank -> Cache Result.
        """
        if not filters:
            filters = {}

        # 1. Check Redis Cache
        if self.redis_client:
            try:
                cache_key = self._get_cache_key(query, filters)
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    logger.info("Cache hit! Returning cached results.")
                    return json.loads(cached_result)
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")

        if not self.vector_store:
            logger.error("Vector store not initialized.")
            return []

        logger.info(f"Searching for: '{query}' with filters: {filters}")

        # 2. Pre-Filtering & Vector Search
        # LangChain MongoDB `similarity_search` supports pre-filtering dict
        # The filter structure must match the Atlas Search filter syntax
        try:
            # We fetch more candidates (top_k) for re-ranking
            results = self.vector_store.similarity_search(
                query,
                k=top_k,
                pre_filter=filters # Ensure this matches pymongo/atlas syntax
            )
            
            # Convert Document objects to dicts for easier handling
            docs = []
            for r in results:
                docs.append({
                    "page_content": r.page_content,
                    "metadata": r.metadata
                })

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

        # 3. Re-Ranking
        final_results = self.rerank_results(query, docs, top_n=top_n)

        # 4. Cache Results (1 hour = 3600 seconds)
        if self.redis_client:
            try:
                self.redis_client.setex(cache_key, 3600, json.dumps(final_results))
            except Exception as e:
                logger.warning(f"Cache write failed: {e}")
        
        return final_results

if __name__ == "__main__":
    # Test Block
    service = VectorService()
    
    # Create index first
    service.create_index()

    # Dummy Data Seeding (only if collection is empty, for testing)
    if service.collection is not None and service.collection.count_documents({}) == 0:
        logger.info("Seeding dummy data for testing...")
        texts = [
            "Solar farm in Vietnam proving high renewable output.",
            "Coal plant optimization in Indonesia.",
            "Wind energy project in Thailand coastal region.",
            "Tech park construction in Singapore.",
            "Community solar project in Philippines."
        ]
        metadatas = [
            {"industry": "Energy", "region": "Southeast Asia", "esg_impact": 0.9, "roi_potential": 0.7},
            {"industry": "Energy", "region": "Southeast Asia", "esg_impact": 0.2, "roi_potential": 0.8},
            {"industry": "Energy", "region": "Southeast Asia", "esg_impact": 0.85, "roi_potential": 0.6},
            {"industry": "Real Estate", "region": "Southeast Asia", "esg_impact": 0.4, "roi_potential": 0.9},
            {"industry": "Energy", "region": "Southeast Asia", "esg_impact": 0.95, "roi_potential": 0.5},
        ]
        
        # In a real scenario we'd use vector_store.add_texts, but that requires calling the embedding API
        # Let's hope the user can authorize the calls or we use a local model.
        # Check: we are using HuggingFaceBgeEmbeddings which runs locally/downloads model.
        service.vector_store.add_texts(texts, metadatas=metadatas)
        logger.info("Seeded 5 documents.")

    # 5. Run Test Query
    query = "Renewable energy project in Southeast Asia"
    # Filter for Energy industry to demonstrate pre-filtering
    # Note: Mongo filter syntax might be simple key-value for specific drivers, 
    # but Atlas Search usually needs specific MQL. LangChain usually adapts dicts.
    test_filter = {"industry": "Energy"} 
    
    results = service.search_projects(query, filters=test_filter, top_k=5, top_n=3)
    
    print("\n--- Top 3 Results for Query: '{}' ---".format(query))
    for i, res in enumerate(results):
        print(f"{i+1}. [Score: {res.get('combined_score', 0):.4f}] {res['page_content']}")
        print(f"   (Relevance: {res.get('relevance_score'):.4f}, ESG: {res['metadata'].get('esg_impact')}, ROI: {res['metadata'].get('roi_potential')})")
