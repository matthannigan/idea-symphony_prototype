from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from shared.models import (
    IdeaInput, BrainstormingContext, BrainstormQuestions,
    BrainstormResponse, BrainstormSynthesis
)
from .idea_symphony import IdeaSymphony
from typing import List, Dict, Any

app = FastAPI(title="Idea Symphony API")

# Load environment variables
from dotenv import load_dotenv
import os
load_dotenv()

# Add Logfire logging
import logfire
logfire.configure(token=os.getenv('LOGFIRE_TOKEN'))
logfire.instrument_pydantic_ai()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize IdeaSymphony
idea_symphony = IdeaSymphony()

@app.post("/api/create-context", response_model=BrainstormingContext)
async def create_context(input_data: IdeaInput):
    try:
        return await idea_symphony.create_context(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-questions", response_model=List[BrainstormQuestions])
async def generate_questions(
    context: BrainstormingContext,
    model_count: int = 1
):
    try:
        return await idea_symphony.generate_questions(context, model_count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/synthesize-questions", response_model=BrainstormQuestions)
async def synthesize_questions(question_sets: List[BrainstormQuestions]):
    try:
        return await idea_symphony.synthesize_questions(question_sets)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chunk-questions", response_model=List[Dict[str, Any]])
async def chunk_questions(questions: BrainstormQuestions):
    try:
        return await idea_symphony.chunk_questions(questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/brainstorm", response_model=List[List[BrainstormResponse]])
async def brainstorm(
    context: BrainstormingContext,
    question_chunks: List[Dict[str, Any]],
    participant_count: int = 2
):
    try:
        return await idea_symphony.brainstorm_responses(
            context, 
            question_chunks, 
            participant_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/synthesize", response_model=BrainstormSynthesis)
async def synthesize(all_responses: List[List[BrainstormResponse]]):
    try:
        return await idea_symphony.synthesize_responses(all_responses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
