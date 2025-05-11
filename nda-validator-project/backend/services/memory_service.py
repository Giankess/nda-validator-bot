import chromadb
from chromadb.config import Settings
import json
from typing import Dict, Any, List
import os
from datetime import datetime

class MemoryService:
    def __init__(self):
        self.client = chromadb.Client(Settings(
            persist_directory="memory",
            anonymized_telemetry=False
        ))
        
        # Create or get collections
        self.nda_collection = self.client.get_or_create_collection("ndas")
        self.feedback_collection = self.client.get_or_create_collection("feedback")
        
        # Ensure memory directory exists
        os.makedirs("memory", exist_ok=True)

    async def save_document(self, document_id: str, content: str, metadata: Dict[str, Any]):
        """Save an NDA document to the memory system."""
        self.nda_collection.add(
            documents=[content],
            metadatas=[{
                **metadata,
                "timestamp": datetime.now().isoformat(),
                "document_id": document_id
            }],
            ids=[document_id]
        )

    async def save_feedback(self, document_id: str, feedback: Dict[str, Any]):
        """Save user feedback to the memory system."""
        feedback_id = f"{document_id}_feedback_{datetime.now().isoformat()}"
        self.feedback_collection.add(
            documents=[json.dumps(feedback)],
            metadatas=[{
                "document_id": document_id,
                "timestamp": datetime.now().isoformat(),
                "sentiment": feedback.get("sentiment", 0)
            }],
            ids=[feedback_id]
        )

    async def get_document_history(self, document_id: str) -> List[Dict[str, Any]]:
        """Retrieve the history of a document including all feedback."""
        # Get the document
        document = self.nda_collection.get(
            where={"document_id": document_id}
        )
        
        # Get all feedback for this document
        feedback = self.feedback_collection.get(
            where={"document_id": document_id}
        )
        
        return {
            "document": document,
            "feedback": feedback
        }

    async def search_similar_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents in the memory system."""
        results = self.nda_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results

    async def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get statistics about feedback patterns."""
        all_feedback = self.feedback_collection.get()
        
        if not all_feedback["metadatas"]:
            return {
                "total_feedback": 0,
                "average_sentiment": 0,
                "feedback_by_month": {}
            }
        
        # Calculate statistics
        sentiments = [f["sentiment"] for f in all_feedback["metadatas"]]
        feedback_by_month = {}
        
        for feedback in all_feedback["metadatas"]:
            month = datetime.fromisoformat(feedback["timestamp"]).strftime("%Y-%m")
            feedback_by_month[month] = feedback_by_month.get(month, 0) + 1
        
        return {
            "total_feedback": len(sentiments),
            "average_sentiment": sum(sentiments) / len(sentiments),
            "feedback_by_month": feedback_by_month
        }

    async def clear_old_documents(self, days_threshold: int = 365):
        """Clear documents and feedback older than the threshold."""
        current_time = datetime.now()
        
        # Get all documents
        all_documents = self.nda_collection.get()
        
        # Filter out old documents
        for doc_id, metadata in zip(all_documents["ids"], all_documents["metadatas"]):
            doc_time = datetime.fromisoformat(metadata["timestamp"])
            if (current_time - doc_time).days > days_threshold:
                self.nda_collection.delete(ids=[doc_id])
                
                # Also delete associated feedback
                feedback = self.feedback_collection.get(
                    where={"document_id": metadata["document_id"]}
                )
                if feedback["ids"]:
                    self.feedback_collection.delete(ids=feedback["ids"]) 