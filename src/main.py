from dotenv import load_dotenv
load_dotenv()

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from src.api.routes.HealthCheck import health_check_router
from src.api.routes.ClearDB import clear_db_router
from src.api.routes.RagQuery import rag_query_router
from src.api.routes.TestEndpoint import rag_pipeline_router
from src.api.routes.CustomLangGraphTesting import rag_pipeline_router as custom_lang_graph_router

from src.core.neo4j_database.neo4j_service import get_neo4j_service, close_neo4j_service
from src.core.mysql_database.mysql_service import get_mysql_service, close_mysql_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    get_neo4j_service()
    print("Neo4j connection Initiated")
    get_mysql_service()
    print("MySQL connection Initiated")

    yield

    close_neo4j_service()
    print("Closing neo4j connection")
    close_mysql_service()
    print("Closing mysql connection")
    
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
app.include_router(custom_lang_graph_router)

static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def serve_chat_interface():
    html_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "Memory-GPT API is running. Place index.html in static folder."}
