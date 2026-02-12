from fastapi.responses import JSONResponse
from fastapi import FastAPI, Form, APIRouter
from dotenv import load_dotenv
import os

load_dotenv()
from src.core.neo4j_database.neo4j_service import get_neo4j_service

rag_query_router = APIRouter(tags=["GraphRag"])

app = FastAPI()

@rag_query_router.put("/neo4j-rag-query")
async def rag_query(
    query: str = Form(...)
):
    """
    Execute RAG query against the Neo4j knowledge graph and return the answer.
    """


    manager = get_neo4j_service()
    answer = manager.run_rag_query(
        db_name=os.getenv("NEO4J_DATABASE", "vector"),
        query=query
    )

    
    return JSONResponse(content={"message": str(answer)})

