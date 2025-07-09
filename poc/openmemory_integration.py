#!/usr/bin/env python3
"""
OpenMemory Integration Proof of Concept for MCP System
====================================================

This module demonstrates how OpenMemory can be integrated into the MCP system
architecture, showing the key integration points and implementation patterns.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import hashlib
import numpy as np
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Memory:
    """Represents a memory object in the OpenMemory system."""
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    timestamp: datetime
    source: str
    importance: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary for serialization."""
        return asdict(self)


@dataclass
class Context:
    """Represents operational context in the MCP system."""
    id: str
    active_memories: List[Memory]
    current_operation: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def add_memory(self, memory: Memory) -> None:
        """Add a memory to the current context."""
        self.active_memories.append(memory)
        
    def get_relevant_memories(self, query: str, limit: int = 5) -> List[Memory]:
        """Get memories relevant to the current query."""
        # Simplified relevance scoring
        relevant = []
        for memory in self.active_memories:
            if query.lower() in memory.content.lower():
                relevant.append(memory)
        return relevant[:limit]


class EmbeddingEngine:
    """Simple embedding engine for demonstration purposes."""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        
    def encode(self, text: str) -> List[float]:
        """Create a simple embedding for text (placeholder implementation)."""
        # In real implementation, use sentence-transformers or OpenAI embeddings
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert hash to pseudo-embedding
        embedding = []
        for i in range(0, min(len(hash_hex), self.dimension * 8), 8):
            chunk = hash_hex[i:i+8]
            value = int(chunk, 16) / (16**8)  # Normalize to 0-1
            embedding.append(value)
            
        # Pad or truncate to desired dimension
        while len(embedding) < self.dimension:
            embedding.append(0.0)
        return embedding[:self.dimension]
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings."""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return np.dot(vec1, vec2) / (norm1 * norm2)


class MemoryStore:
    """Core memory storage and retrieval system."""
    
    def __init__(self, embedding_engine: EmbeddingEngine):
        self.embedding_engine = embedding_engine
        self.memories: Dict[str, Memory] = {}
        self.index_by_source: Dict[str, List[str]] = {}
        
    def create_memory(self, content: str, metadata: Dict[str, Any] = None, 
                     source: str = "unknown") -> Memory:
        """Create a new memory from content."""
        metadata = metadata or {}
        
        # Generate embedding
        embedding = self.embedding_engine.encode(content)
        
        # Create memory object
        memory_id = hashlib.sha256(
            f"{content}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        memory = Memory(
            id=memory_id,
            content=content,
            embedding=embedding,
            metadata=metadata,
            timestamp=datetime.now(),
            source=source,
            importance=metadata.get('importance', 0.5)
        )
        
        # Store memory
        self.memories[memory_id] = memory
        
        # Update source index
        if source not in self.index_by_source:
            self.index_by_source[source] = []
        self.index_by_source[source].append(memory_id)
        
        logger.info(f"Created memory {memory_id} from source {source}")
        return memory
    
    def retrieve_memories(self, query: str, limit: int = 10) -> List[Memory]:
        """Retrieve memories based on semantic similarity."""
        if not self.memories:
            return []
            
        query_embedding = self.embedding_engine.encode(query)
        
        # Calculate similarities
        similarities = []
        for memory_id, memory in self.memories.items():
            similarity = self.embedding_engine.similarity(
                query_embedding, memory.embedding
            )
            similarities.append((similarity, memory))
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [memory for _, memory in similarities[:limit]]
    
    def get_memories_by_source(self, source: str) -> List[Memory]:
        """Get all memories from a specific source."""
        memory_ids = self.index_by_source.get(source, [])
        return [self.memories[mid] for mid in memory_ids if mid in self.memories]
    
    def update_memory_importance(self, memory_id: str, importance: float) -> None:
        """Update the importance score of a memory."""
        if memory_id in self.memories:
            self.memories[memory_id].importance = importance
            
    def consolidate_memories(self) -> int:
        """Consolidate memories by removing duplicates and low-importance items."""
        initial_count = len(self.memories)
        
        # Remove low-importance memories (importance < 0.3)
        to_remove = []
        for memory_id, memory in self.memories.items():
            if memory.importance < 0.3:
                to_remove.append(memory_id)
        
        for memory_id in to_remove:
            self.remove_memory(memory_id)
        
        removed_count = initial_count - len(self.memories)
        logger.info(f"Consolidated {removed_count} memories")
        return removed_count
    
    def remove_memory(self, memory_id: str) -> bool:
        """Remove a memory from the store."""
        if memory_id in self.memories:
            memory = self.memories[memory_id]
            del self.memories[memory_id]
            
            # Update source index
            if memory.source in self.index_by_source:
                self.index_by_source[memory.source].remove(memory_id)
            
            return True
        return False


class FileSystemConnector:
    """Connects filesystem operations to memory creation."""
    
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store
        self.file_handlers = {}
        
    def register_file_handler(self, extension: str, handler):
        """Register a content handler for specific file extensions."""
        self.file_handlers[extension] = handler
        
    def on_file_created(self, file_path: str, content: str, metadata: Dict[str, Any] = None):
        """Handle file creation event."""
        metadata = metadata or {}
        metadata.update({
            'file_path': file_path,
            'operation': 'created',
            'file_size': len(content),
            'file_extension': Path(file_path).suffix
        })
        
        # Create memory from file content
        memory = self.memory_store.create_memory(
            content=content,
            metadata=metadata,
            source='filesystem'
        )
        
        logger.info(f"Created memory for file: {file_path}")
        return memory
    
    def on_file_modified(self, file_path: str, content: str, metadata: Dict[str, Any] = None):
        """Handle file modification event."""
        metadata = metadata or {}
        metadata.update({
            'file_path': file_path,
            'operation': 'modified',
            'file_size': len(content),
            'file_extension': Path(file_path).suffix
        })
        
        # Create new memory for modified content
        memory = self.memory_store.create_memory(
            content=content,
            metadata=metadata,
            source='filesystem'
        )
        
        logger.info(f"Updated memory for file: {file_path}")
        return memory
    
    def on_file_deleted(self, file_path: str):
        """Handle file deletion event."""
        # Find and remove memories associated with this file
        filesystem_memories = self.memory_store.get_memories_by_source('filesystem')
        
        removed_count = 0
        for memory in filesystem_memories:
            if memory.metadata.get('file_path') == file_path:
                self.memory_store.remove_memory(memory.id)
                removed_count += 1
                
        logger.info(f"Removed {removed_count} memories for deleted file: {file_path}")


class GraphRAGConnector:
    """Connects OpenMemory to GraphRAG system."""
    
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store
        self.entity_cache = {}
        self.relation_cache = {}
        
    def extract_entities(self, content: str) -> List[str]:
        """Extract entities from content (simplified implementation)."""
        # In real implementation, use NLP libraries like spaCy or NLTK
        words = content.split()
        entities = []
        
        for word in words:
            if word.istitle() and len(word) > 2:
                entities.append(word)
                
        return list(set(entities))
    
    def extract_relations(self, content: str) -> List[Dict[str, str]]:
        """Extract relations from content (simplified implementation)."""
        # Simplified relation extraction
        relations = []
        words = content.split()
        
        for i, word in enumerate(words):
            if word.lower() in ['is', 'has', 'contains', 'relates', 'connects']:
                if i > 0 and i < len(words) - 1:
                    relations.append({
                        'subject': words[i-1],
                        'predicate': word,
                        'object': words[i+1]
                    })
                    
        return relations
    
    def build_graph_from_memories(self) -> Dict[str, Any]:
        """Build knowledge graph from stored memories."""
        entities = set()
        relations = []
        
        for memory in self.memory_store.memories.values():
            memory_entities = self.extract_entities(memory.content)
            memory_relations = self.extract_relations(memory.content)
            
            entities.update(memory_entities)
            relations.extend(memory_relations)
        
        graph = {
            'entities': list(entities),
            'relations': relations,
            'memory_count': len(self.memory_store.memories)
        }
        
        logger.info(f"Built graph with {len(entities)} entities and {len(relations)} relations")
        return graph
    
    def memory_enhanced_query(self, query: str, context: Context) -> Dict[str, Any]:
        """Process query with memory context enhancement."""
        # Retrieve relevant memories
        relevant_memories = self.memory_store.retrieve_memories(query, limit=5)
        
        # Build context from memories
        context_entities = set()
        context_relations = []
        
        for memory in relevant_memories:
            memory_entities = self.extract_entities(memory.content)
            memory_relations = self.extract_relations(memory.content)
            
            context_entities.update(memory_entities)
            context_relations.extend(memory_relations)
        
        # Enhanced query result
        result = {
            'query': query,
            'relevant_memories': len(relevant_memories),
            'context_entities': list(context_entities),
            'context_relations': context_relations,
            'memory_sources': [m.source for m in relevant_memories]
        }
        
        return result


class MCPSystem:
    """Main MCP system integrating OpenMemory."""
    
    def __init__(self):
        self.embedding_engine = EmbeddingEngine()
        self.memory_store = MemoryStore(self.embedding_engine)
        self.filesystem_connector = FileSystemConnector(self.memory_store)
        self.graphrag_connector = GraphRAGConnector(self.memory_store)
        self.current_context = Context(
            id="default",
            active_memories=[],
            current_operation="idle"
        )
        
    def process_file(self, file_path: str, content: str) -> Memory:
        """Process a file and create memory."""
        return self.filesystem_connector.on_file_created(file_path, content)
    
    def query_system(self, query: str) -> Dict[str, Any]:
        """Query the system with memory enhancement."""
        # Update context
        self.current_context.current_operation = "query"
        
        # Get enhanced query result
        result = self.graphrag_connector.memory_enhanced_query(query, self.current_context)
        
        # Add relevant memories to context
        relevant_memories = self.memory_store.retrieve_memories(query, limit=3)
        for memory in relevant_memories:
            self.current_context.add_memory(memory)
        
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            'total_memories': len(self.memory_store.memories),
            'memories_by_source': {
                source: len(memory_ids) 
                for source, memory_ids in self.memory_store.index_by_source.items()
            },
            'context_memories': len(self.current_context.active_memories),
            'current_operation': self.current_context.current_operation
        }


# Example usage and demonstration
async def demonstrate_integration():
    """Demonstrate the OpenMemory integration with MCP system."""
    print("=== OpenMemory Integration Demonstration ===\\n")
    
    # Initialize system
    mcp_system = MCPSystem()
    
    # Simulate file operations
    print("1. Processing files...")
    file_contents = [
        ("document1.txt", "This is a research paper about artificial intelligence and machine learning."),
        ("document2.txt", "OpenMemory is a system for managing AI memory and context."),
        ("document3.txt", "GraphRAG combines graph databases with retrieval augmented generation."),
        ("code.py", "def process_data(data): return data.transform().analyze()"),
    ]
    
    for file_path, content in file_contents:
        memory = mcp_system.process_file(file_path, content)
        print(f"  Created memory {memory.id} for {file_path}")
    
    # Query system
    print("\\n2. Querying system...")
    queries = [
        "What is artificial intelligence?",
        "How does OpenMemory work?",
        "Show me code examples",
        "What are the system capabilities?"
    ]
    
    for query in queries:
        result = mcp_system.query_system(query)
        print(f"  Query: {query}")
        print(f"  Found {result['relevant_memories']} relevant memories")
        print(f"  Context entities: {result['context_entities'][:3]}...")
        print()
    
    # Show system status
    print("3. System Status:")
    status = mcp_system.get_system_status()
    print(f"  Total memories: {status['total_memories']}")
    print(f"  Memories by source: {status['memories_by_source']}")
    print(f"  Context memories: {status['context_memories']}")
    
    # Demonstrate memory consolidation
    print("\\n4. Memory Consolidation:")
    # Artificially lower importance of some memories
    for memory_id in list(mcp_system.memory_store.memories.keys())[:2]:
        mcp_system.memory_store.update_memory_importance(memory_id, 0.2)
    
    removed_count = mcp_system.memory_store.consolidate_memories()
    print(f"  Removed {removed_count} low-importance memories")
    
    # Final status
    final_status = mcp_system.get_system_status()
    print(f"  Final memory count: {final_status['total_memories']}")
    
    print("\\n=== Demonstration Complete ===")


if __name__ == "__main__":
    asyncio.run(demonstrate_integration())