from fastapi.responses import JSONResponse
from fastapi import FastAPI, Form, APIRouter
from dotenv import load_dotenv
import uuid

from src.core.agent_logic.agent import chat_agent

load_dotenv()

rag_pipeline_router = APIRouter(tags=["GraphRag"])
app = FastAPI()

@rag_pipeline_router.post("/dynamic-kg-query")
async def dynamic_kg_query(
    query: str = Form(...),
    session_id: str = Form(None)  
):
    """
    Process a user query using the dynamic knowledge graph agent.
    If session_id is provided, conversation history is maintained across calls.
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    response = await chat_agent(session_id, query)

    return JSONResponse(content={
        "answer": response,
        "session_id": session_id
    })
