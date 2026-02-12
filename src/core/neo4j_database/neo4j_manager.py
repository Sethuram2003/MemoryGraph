from neo4j import GraphDatabase, basic_auth
from neo4j_graphrag.embeddings import AzureOpenAIEmbeddings
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.llm import AzureOpenAILLM
from neo4j_graphrag.retrievers import VectorCypherRetriever
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.indexes import create_vector_index
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import FixedSizeSplitter

import os
import asyncio

from src.core.neo4j_database.prompts import rag_template, PROMPT_TEMPLATE, DEFAULT_TEMPLATE
from src.core.neo4j_database.schema import GRAPH_SCHEMA
from dotenv import load_dotenv

load_dotenv()

class Neo4jDBManager:
    def __init__(self, uri, admin_user, admin_password, db_name):
        """
        Initialize the Neo4jDBManager with admin credentials.
        """
        self.uri = uri
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.driver = GraphDatabase.driver(
            self.uri, auth=basic_auth(self.admin_user, self.admin_password), database=db_name
        )

    def create_database(self, db_name):
        """
        Create a new database with the given name.
        """
        with self.driver.session(database="system") as session:
            try:
                session.run(f"CREATE DATABASE {db_name} IF NOT EXISTS")
                print(f"Database '{db_name}' created successfully.")
            except Exception as e:
                print(f"Error creating database '{db_name}': {e}")

    def delete_database(self, db_name):
        """
        Delete a database with the given name.
        """
        with self.driver.session(database="system") as session:
            try:
                session.run(f"DROP DATABASE {db_name} IF EXISTS")
                print(f"Database '{db_name}' deleted successfully.")
            except Exception as e:
                print(f"Error deleting database '{db_name}': {e}")

    def clear_database(self, db_name: str):
        """
        Clear all nodes and relationships from the given database.
        DOES NOT delete the database itself.
        """
        with self.driver.session(database=db_name) as session:
            try:
                session.run("MATCH (n) DETACH DELETE n")
                print(f"Database '{db_name}' cleared successfully.")
            except Exception as e:
                print(f"Error clearing database '{db_name}': {e}")

    def close(self):
        """
        Close the driver connection.
        """
        self.driver.close()

    async def pipe_line_text(self, db_name: str, text: str):
        """
        create a KG and populate the database from text
        """

        azure_embedding = AzureOpenAIEmbeddings(
                                    model=os.getenv("DEPLOYMENT"),
                                    api_key= os.getenv("API_KEY"), 
                                    azure_endpoint=os.getenv("API_ENDPOINT"),
                                    api_version=os.getenv("API_VERSION")
                                )

        llm = AzureOpenAILLM(
                                model_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),           
                                api_key= os.getenv("AZURE_OPENAI_API_KEY"), 
                                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                api_version="2024-08-01-preview",
                            )


        kg_builder = SimpleKGPipeline(
                    llm=llm,
                    driver=self.driver,
                    text_splitter=FixedSizeSplitter(chunk_size=800, chunk_overlap=100),
                    embedder=azure_embedding,
                    neo4j_database=db_name,
                    # prompt_template=PROMPT_TEMPLATE,
                    # schema="EXTRACTED",
                    schema=GRAPH_SCHEMA,
                    from_pdf=False
                    )

        await kg_builder.run_async(text=text)
        print("Finished KG construction from text.")

    
    async def pipe_line(self, db_name: str, path: str):
        """
        create a KG and populate the database
        """

        azure_embedding = AzureOpenAIEmbeddings(
                                    model=os.getenv("DEPLOYMENT"),
                                    api_key= os.getenv("API_KEY"), 
                                    azure_endpoint=os.getenv("API_ENDPOINT"),
                                    api_version=os.getenv("API_VERSION")
                                )
        
        test_embedding = azure_embedding.embed_query("test")
        actual_dimensions = len(test_embedding)
        print(actual_dimensions)

        llm = AzureOpenAILLM(
                                model_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),           
                                api_key= os.getenv("AZURE_OPENAI_API_KEY"), 
                                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                api_version="2024-08-01-preview",
                            )


        kg_builder = SimpleKGPipeline(
                    llm=llm,
                    prompt_template=DEFAULT_TEMPLATE,
                    driver=self.driver,
                    text_splitter=FixedSizeSplitter(chunk_size=800, chunk_overlap=100),
                    embedder=azure_embedding,
                    from_pdf=True,
                    neo4j_database=db_name
                    )

        await kg_builder.run_async(file_path=path)
        print("Finished KG construction.")


    def run_rag_query(self, db_name: str, query: str):
        """
        Run a RAG query against the specified database.
        """

        INDEX_NAME = f"{db_name}_chunk_index"
        azure_embedding = AzureOpenAIEmbeddings(
                                    model=os.getenv("DEPLOYMENT"),
                                    api_key= os.getenv("API_KEY"), 
                                    azure_endpoint=os.getenv("API_ENDPOINT"),
                                    api_version=os.getenv("API_VERSION")
                                )

        llm = AzureOpenAILLM(
                                model_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                                api_key= os.getenv("AZURE_OPENAI_API_KEY"), 
                                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                api_version="2024-08-01-preview",
                            )
        
        try:
            create_vector_index(
                self.driver,
                name=INDEX_NAME,
                label="Chunk",
                embedding_property="embedding",
                dimensions=3072,
                similarity_fn="cosine",
                neo4j_database=db_name
            )
            print(f"Vector index '{INDEX_NAME}' created.")
        except Exception as e:
            print(f"Index may already exist: {e}")

        retriever = VectorCypherRetriever(
                        self.driver,
                        index_name=INDEX_NAME,
                        neo4j_database=db_name,
                        embedder=azure_embedding,
                        retrieval_query="""
                                        //1) Go out 2-3 hops in the entity graph and get relationships
                                        WITH node AS chunk
                                        MATCH (chunk)<-[:FROM_CHUNK]-(entity)-[relList:!FROM_CHUNK]-{1,2}(nb)
                                        UNWIND relList AS rel

                                        //2) collect relationships and text chunks
                                        WITH collect(DISTINCT chunk) AS chunks, collect(DISTINCT rel) AS rels

                                        //3) format and return context - without details property
                                        RETURN apoc.text.join([c in chunks | c.text], '\n') +
                                        apoc.text.join([r in rels |
                                        startNode(r).name + ' - ' + type(r) + ' -> ' + endNode(r).name],
                                        '\n') AS info
                                        """
                    )
        
        rag = GraphRAG(
            retriever=retriever,
            llm=llm,
            prompt_template=rag_template
        )

        print("Running RAG query...")
        response = rag.search(
            query_text=query,
            retriever_config={"top_k": 5}
        )

        return response.answer


async def main():
    uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
    admin_user = os.getenv("NEO4J_USERNAME", "neo4j")
    admin_password = os.getenv("NEO4J_PASSWORD", "12345678")
    database = os.getenv("NEO4J_DATABASE", "chat_memory_graph")

    manager = Neo4jDBManager(uri, admin_user, admin_password, database)

    # manager.clear_database(database)

    manager.close()

if __name__ == "__main__":
    asyncio.run(main())
