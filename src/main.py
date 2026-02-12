from dotenv import load_dotenv
load_dotenv()

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.api.routes.HealthCheck import health_check_router
from src.api.routes.ClearDB import clear_db_router
from src.api.routes.RagQuery import rag_query_router
from src.api.routes.TestEndpoint import rag_pipeline_router

from src.core.neo4j_database.neo4j_service import get_neo4j_service, close_neo4j_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    get_neo4j_service()
    print("Neo4j connection Initiated")

    yield

    close_neo4j_service()
    print("Closing neo4j connection")
    
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_check_router)
app.include_router(clear_db_router)
app.include_router(rag_query_router)
app.include_router(rag_pipeline_router)
