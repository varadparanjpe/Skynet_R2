import faiss
import numpy as np
import json
import os

class VectorMemoryFAISS:
    """
    Long-Term Memory implementing Semantic Retrieval (Guardrail 6 + Learning Loop foundation).
    In this hackathon architecture, we use FAISS to store vector embeddings of past shipment contexts
    to find 'similar historical situations' without needing an external cloud DB.
    """
    def __init__(self, dimension=128):
        self.dimension = dimension
        self.index_file = "backend/memory/faiss_index.bin"
        self.meta_file = "backend/memory/faiss_meta.json"
        
        # Load or initialize FAISS index
        if os.path.exists(self.index_file) and os.path.exists(self.meta_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.meta_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.index = faiss.IndexFlatL2(dimension)
            self.metadata = []

    def _mock_embedding(self, shipment_dict: dict) -> np.ndarray:
        """
        In a real application, this would call `openai.Embedding.create()` or `sentence-transformers`.
        For local hackathon speed, we deterministically hash the key metrics into a fixed dimension vector.
        """
        # Create a deterministc pseudo-embedding based on continuous features
        features = [
            shipment_dict.get('distance_remaining_km', 0) / 2000.0,
            shipment_dict.get('weather_risk', 0),
            shipment_dict.get('traffic_risk', 0),
            shipment_dict.get('carrier_reliability', 0),
            shipment_dict.get('port_hub_queue_time_mins', 0) / 100.0
        ]
        
        # Tile it out to 128 dimensions and add some deterministic noise to simulate text embedding spread
        vec = np.tile(features, self.dimension // len(features) + 1)[:self.dimension]
        vec = vec / np.linalg.norm(vec) # Normalize
        return np.array([vec], dtype=np.float32)

    def add_experience(self, shipment_context: dict, decision: str, outcome_rating: str):
        """
        Stores the past shipment and its outcome in long term memory.
        """
        vec = self._mock_embedding(shipment_context)
        self.index.add(vec)
        
        record = {
            "shipment_id": shipment_context['shipment_id'],
            "context": shipment_context,
            "decision": decision,
            "outcome": outcome_rating
        }
        self.metadata.append(record)
        
        # Save to disk
        os.makedirs('backend/memory', exist_ok=True)
        faiss.write_index(self.index, self.index_file)
        with open(self.meta_file, 'w') as f:
            json.dump(self.metadata, f)

    def retrieve_similar(self, current_context: dict, top_k=3) -> list:
        """
        Query the memory for similar past situations to inform the Agent's reasoning.
        """
        if self.index.ntotal == 0:
            return []
            
        vec = self._mock_embedding(current_context)
        distances, indices = self.index.search(vec, min(top_k, self.index.ntotal))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:
                results.append({
                    "distance": float(distances[0][i]),
                    "record": self.metadata[idx]
                })
        return results
