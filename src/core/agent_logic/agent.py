import asyncio
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain.tools import tool

from src.core.mysql_database.mysql_service import get_mysql_service, close_mysql_service
from src.core.neo4j_database.neo4j_service import get_neo4j_service
from src.core.agent_logic.prompts import SYSTEM_PROMPT, SYSTEM_PROMPT_WITH_RAG

def db_messages_to_langchain(messages):
    """Convert list of dicts from DB to LangChain message list."""
    lc_messages = []
    for msg in messages:
        if msg["sender_type"] == "user":
            lc_messages.append({"role": "user", "content": msg["message"]})
        else:
            lc_messages.append({"role": "assistant", "content": msg["message"]})
    return lc_messages

async def chat_agent(session_id: str, user_input: str) -> str:
    """
    Process a user input, using the last 5 messages from the database as context.
    Returns the agent's response.
    """
    manager = get_mysql_service()

    total_messages = manager.get_session_history(session_id)

    chat_history_length = len(total_messages)

    if chat_history_length >= 10 and chat_history_length % 10 == 0:
        graphrag_messages = manager.get_session_history(
            session_identifier=session_id,
            limit=10,
            order="desc"
        )
        graphrag_messages.reverse()

        graph_manager = get_neo4j_service()
        try:
            graph_manager.create_database(session_id)
        except Exception as e:
            print(f"Error creating Neo4j database for session {session_id}: {e}")
        
        await graph_manager.pipe_line_text(
            session_id,
            "\n".join([msg["message"] for msg in graphrag_messages if msg["sender_type"] in ("user", "agent")])
        )
        

        print(f"Graph updated for session {session_id} with latest 15 messages.")



    recent_messages = manager.get_session_history(
        session_identifier=session_id,
        limit=5,
        order="desc"
    )
    recent_messages.reverse() 

    history = db_messages_to_langchain(recent_messages)

    history.append({"role": "user", "content": user_input})

    llm = ChatOllama(model="kimi-k2:1t-cloud")

    if chat_history_length > 10:
        @tool
        def chat_history_tool(query: str) -> str:
            """ Tool to query the Neo4j knowledge graph using RAG and return the answer. from the chat history. """

            pipeline = get_neo4j_service()
            response = pipeline.run_rag_query(
                db_name=session_id,
                query=query
            )

            return response

        agent = create_agent(
            llm,
            tools=[chat_history_tool],
            system_prompt=SYSTEM_PROMPT_WITH_RAG
        )
    else:

        agent = create_agent(
            llm,
            system_prompt=SYSTEM_PROMPT
        )

    response = await agent.ainvoke({"messages": history})
    assistant_reply = response["messages"][-1].content

    manager.store_message(session_id, "user", user_input)
    manager.store_message(session_id, "agent", assistant_reply)

    return assistant_reply

async def main():
    session_id = "test-session-001"   

    print("Starting chat with agent. Type 'exit' or 'quit' to end.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break

        response = await chat_agent(session_id, user_input)
        print(f"Agent: {response}\n")

    close_mysql_service()

if __name__ == "__main__":
    asyncio.run(main())