from neo4j_graphrag.generation import RagTemplate


DEFAULT_TEMPLATE = """
You are a top-tier algorithm designed for extracting a labeled property graph schema in
structured formats.

Generate a generalized graph schema based on the input text. Identify key node types,
their relationship types, and property types.

IMPORTANT RULES:
1. Return only abstract schema information, not concrete instances.
2. Use singular PascalCase labels for node types (e.g., Person, Company, Product).
3. **MANDATORY: Every node type MUST include a property named "name" with the type "STRING".**
4. Use UPPER_SNAKE_CASE labels for relationship types (e.g., WORKS_FOR, MANAGES).
5. Include additional property definitions only when the type can be confidently inferred.
6. When defining patterns, ensure that every node label and relationship label mentioned exists in your lists of node types and relationship types.
7. Do not create node types that aren't clearly mentioned in the text.
8. Keep your schema minimal and focused on clearly identifiable patterns in the text.

Accepted property types are: BOOLEAN, DATE, DURATION, FLOAT, INTEGER, LIST,
LOCAL_DATETIME, LOCAL_TIME, POINT, STRING, ZONED_DATETIME, ZONED_TIME.

Return a valid JSON object that follows this precise structure:
{{
  "node_types": [
    {{
      "label": "NodeLabel",
      "properties": [
        {{
          "name": "name",
          "type": "STRING"
        }},
        ...
      ]
    }},
    ...
  ],
  "relationship_types": [
    {{
      "label": "RELATIONSHIP_TYPE"
    }},
    ...
  ],
  "patterns": [
    ["SourceNode", "RELATIONSHIP_TYPE", "TargetNode"],
    ...
  ]
}}

Examples:
{examples}

Input text:
{text}
"""


PROMPT_TEMPLATE = """
You are a top-tier knowledge engineering algorithm. Your task is to transform travel data into a high-fidelity Knowledge Graph JSON.

### SELECTIVE MERGING RULES
1. **GLOBAL NODES (MERGE):** Use standard names for [Country] and [City] (e.g., "Denmark", "Aarhus"). This allows multiple ports to connect to the same geographic branch.
2. **PRIVATE NODES (DO NOT MERGE):** For [Category], [Activity], [Cuisine], [Shopping], [Museum], [HistoricalSite], and [InsiderTip], you MUST prefix both the 'id' and the 'name' with the Port Name.
   - Example: Instead of name "Local Cuisine", use "Aarhus Port Local Cuisine".
   - Example: Instead of id "local_cuisine", use "AarhusPort_LocalCuisine".
   - This ensures that if two ports have "Local Cuisine", they remain separate nodes.

### HIERARCHY & STRUCTURE
- [Country] -> [City] -> [Port] -> [Category] -> [Leaf Node] -> [Tip].
- Each [Port] MUST have its own unique set of [Category] nodes.
- Each [Category] MUST connect to exactly ONE Port.
- Each [Leaf Node] MUST connect to exactly ONE Category.

### OUTPUT FORMAT
Return ONLY a raw JSON object. No markdown, no backticks.
{{
  "nodes": [
    {{
      "id": "PortName_UniqueNodeID",
      "label": "Entity_Type",
      "properties": {{
        "name": "PortName Specific Name",
        "description": "Contextual summary for this specific port (min 10 words)."
      }}
    }}
  ],
  "relationships": [
    {{
      "type": "RELATIONSHIP_TYPE",
      "start_node_id": "unique_id",
      "end_node_id": "unique_id",
      "properties": {{
        "description": "Why these are linked in this specific port context (min 10 words)."
      }}
    }}
  ]
}}

### CONSTRAINTS
- **Schema:** Use only: {schema}
- **Branding:** Every node below the Port level MUST be "branded" with the Port name in its properties to prevent accidental merging.

Input text:
{text}
"""


rag_template = RagTemplate(template='''Answer the Question using the following Context. Only respond with information mentioned in the Context. Do not inject any speculative information not mentioned.

# Question:
{query_text}

# Context:
{context}

# Answer:
''', expected_inputs=['query_text', 'context'])