from fastapi.responses import JSONResponse
from fastapi import FastAPI, Form, APIRouter
from src.core.neo4j_database.neo4j_service import get_neo4j_service
from dotenv import load_dotenv
from src.core.dynamic_memory_approach.lang_graph import create_workflow
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
import os
import uuid
from langchain.tools import tool

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
    
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "session_id": session_id
    }
    
    config = {"configurable": {"thread_id": session_id}}

    llm = ChatOllama(model=os.getenv("OLLAMA_LLM_MODEL", "kimi-k2:1t-cloud"))

    @tool
    def chat_history_tool(query: str) -> str:
        """ Tool to query the Neo4j knowledge graph using RAG and return the answer. from the chat history. """

        pipeline = get_neo4j_service()
        response = pipeline.run_rag_query(
            db_name=session_id,
            query=query
        )

        return response

    agent = create_workflow(llm=llm, tools=[chat_history_tool])
    
    try:
        final_state = await agent.ainvoke(initial_state, config=config)
        
        last_message = final_state["messages"][-1]
        if hasattr(last_message, "content"):
            answer = last_message.content
        else:
            answer = str(last_message)
        
        return JSONResponse(content={
            "answer": answer,
            "session_id": session_id,
            "kg_built": final_state.get("kg_built", False)
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Agent execution failed: {str(e)}"}
        )