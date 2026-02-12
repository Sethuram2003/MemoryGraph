import os
from src.core.neo4j_database.neo4j_manager import Neo4jDBManager

neo4j_service = None

def get_neo4j_service() -> Neo4jDBManager:
    """FastAPI dependency to get Neo4j service instance"""
    global neo4j_service

    if neo4j_service is None:
        neo4j_service = Neo4jDBManager(
            uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687"),
            admin_user = os.getenv("NEO4J_USERNAME", "neo4j"),
            admin_password = os.getenv("NEO4J_PASSWORD", "password"),
            db_name=os.getenv("NEO4J_DATABASE")
        )
    return neo4j_service

def close_neo4j_service():
    """Close Neo4j service connection"""
    global neo4j_service
    
    neo4j_service.close()