from fastapi.responses import JSONResponse
from fastapi import FastAPI, Form, APIRouter
from src.core.neo4j_database.neo4j_service import get_neo4j_service
from dotenv import load_dotenv

load_dotenv()

import os

rag_pipeline_router = APIRouter(tags=["GraphRag"])

app = FastAPI()

@rag_pipeline_router.post("/neo4j-rag-pipeline-pdf-to-kg")
async def rag_pipeline(
    content: str = Form(...)
):
    """
    Execute RAG pipeline to create and populate knowledge graph in Neo4j database.
    """
    manager = get_neo4j_service()


    await manager.pipe_line_text(
        db_name=os.getenv("NEO4J_DATABASE"),
        text=content
    )


    return JSONResponse(content={"message": "RAG pipeline executed successfully. Knowledge graph updated."})

