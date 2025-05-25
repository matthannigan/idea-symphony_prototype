import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os
from shared.models import (
    IdeaInput, BrainstormingContext, BrainstormQuestions,
    BrainstormResponse, BrainstormSynthesis
)

class IdeaSymphonyClient:
    def __init__(self, base_url: str = "http://localhost:8000", use_mock_data: bool = False):
        self.base_url = base_url
        self.use_mock_data = use_mock_data
        self.client = httpx.AsyncClient(base_url=base_url, timeout=60.0)
        
        # Load mock data if using mock mode
        if self.use_mock_data:
            self.mock_data = self._load_mock_data()
    
    def _load_mock_data(self) -> Dict[str, Any]:
        """Load mock data from JSON file"""
        mock_data_path = os.path.join(os.path.dirname(__file__), "mock_data.json")
        try:
            with open(mock_data_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Return empty mock data if file doesn't exist
            return {
                "create_context": {"context": "Mock context document"},
                "generate_questions": [{
                    "question_groups": [{
                        "heading": "Mock Questions",
                        "questions": [
                            {
                                "short_summary": "Mock Question 1",
                                "full_description": "This is a mock question for testing"
                            }
                        ]
                    }]
                }],
                "synthesize_questions": {
                    "question_groups": [{
                        "heading": "Mock Synthesized Questions",
                        "questions": [
                            {
                                "short_summary": "Mock Synthesized Question",
                                "full_description": "This is a mock synthesized question"
                            }
                        ]
                    }]
                },
                "chunk_questions": [{
                    "heading": "Mock Chunk",
                    "questions": [
                        {
                            "short_summary": "Mock Chunked Question",
                            "full_description": "This is a mock chunked question"
                        }
                    ]
                }],
                "brainstorm": [[{
                    "question": "Mock Question",
                    "answers": ["Mock answer 1", "Mock answer 2"]
                }]],
                "synthesize": {
                    "synthesized_content": "Mock synthesized content",
                    "attributed_content": "Mock attributed content"
                }
            }
    
    async def _get_mock_response(self, endpoint: str) -> Any:
        """Get mock response for an endpoint"""
        if endpoint in self.mock_data:
            return self.mock_data[endpoint]
        raise ValueError(f"No mock data available for endpoint: {endpoint}")
    
    async def create_context(self, idea_text: str, document_content: Optional[str] = None) -> Dict[str, Any]:
        """Create a context document from the user's input"""
        if self.use_mock_data:
            return await self._get_mock_response("create_context")
            
        response = await self.client.post(
            "/api/create-context",
            json={
                "idea_text": idea_text,
                "document_content": document_content
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def generate_questions(self, context: BrainstormingContext, model_count: int = 1) -> List[Dict[str, Any]]:
        """Generate brainstorming questions"""
        if self.use_mock_data:
            return await self._get_mock_response("generate_questions")
        payload = context.dict()
        payload["model_count"] = model_count
        response = await self.client.post(
            "/api/generate-questions",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def synthesize_questions(self, question_sets: List[BrainstormQuestions]) -> Dict[str, Any]:
        """Synthesize multiple question sets into one"""
        if self.use_mock_data:
            return await self._get_mock_response("synthesize_questions")
        payload = [qs.dict() for qs in question_sets]
        response = await self.client.post(
            "/api/synthesize-questions",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def chunk_questions(self, questions: BrainstormQuestions) -> List[Dict[str, Any]]:
        """Chunk questions into groups"""
        if self.use_mock_data:
            return await self._get_mock_response("chunk_questions")
        payload = questions.dict()
        response = await self.client.post(
            "/api/chunk-questions",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def brainstorm(
        self,
        context: BrainstormingContext,
        question_chunks: List[Dict[str, Any]],
        participant_count: int = 2
    ) -> List[List[Dict[str, Any]]]:
        """Generate brainstorming responses"""
        if self.use_mock_data:
            return await self._get_mock_response("brainstorm")
        payload = {
            "context": context.dict(),
            "question_chunks": question_chunks,
            "participant_count": participant_count
        }
        response = await self.client.post(
            "/api/brainstorm",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def synthesize(self, all_responses: List[List[BrainstormResponse]]) -> Dict[str, Any]:
        """Synthesize all brainstorming responses"""
        if self.use_mock_data:
            return await self._get_mock_response("synthesize")
        payload = [[resp.dict() for resp in participant] for participant in all_responses]
        response = await self.client.post(
            "/api/synthesize",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
