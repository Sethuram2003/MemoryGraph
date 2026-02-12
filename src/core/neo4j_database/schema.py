NODE_TYPES = [
    {
        "label": "User", 
        "properties": [
            {"name": "user_id", "type": "STRING", "description": "The unique ID for your single user"},
            {"name": "name", "type": "STRING", "description": "e.g., 'Alex'"},
            {"name": "current_mood", "type": "STRING", "description": "Updated dynamically based on last session"}
        ]
    },
    {
        "label": "Agent", 
        "properties": [
            {"name": "agent_id", "type": "STRING"},
            {"name": "persona_name", "type": "STRING", "description": "e.g., 'Helpful Companion'"}
        ]
    },

    {
        "label": "Session", 
        "properties": [
            {"name": "session_id", "type": "STRING", "description": "Unique UUID for this specific conversation"},
            {"name": "start_time", "type": "DATETIME"},
            {"name": "summary", "type": "STRING", "description": "Auto-generated summary: e.g., 'Chat about nursing job and cat Luna'"},
            {"name": "topic_tags", "type": "LIST<STRING>", "description": "e.g., ['Work', 'Pets', 'Hiking']"}
        ]
    },
    {
        "label": "Message", 
        "properties": [
            {"name": "content", "type": "STRING", "description": "The raw text"},
            {"name": "role", "type": "STRING", "description": "'user' or 'agent'"},
            {"name": "timestamp", "type": "DATETIME"},
            {"name": "sentiment_score", "type": "FLOAT", "description": "-1.0 to 1.0"}
        ]
    },


    {
        "label": "Fact", 
        "properties": [
            {"name": "category", "type": "STRING", "description": "e.g., Occupation, Location, Hobby"},
            {"name": "value", "type": "STRING", "description": "e.g., 'Nurse', 'Seattle', 'Mystery Novels'"},
            {"name": "confidence", "type": "FLOAT"}
        ]
    },
    {
        "label": "Entity", 
        "properties": [
            {"name": "name", "type": "STRING", "description": "e.g., 'Luna', 'Rattlesnake Ledge'"},
            {"name": "type", "type": "STRING", "description": "e.g., Pet, Location, BookGenre"}
        ]
    }
]

RELATIONSHIP_TYPES = [
    {"label": "HAS_SESSION", "description": "User -> Session. The main branch connector."},
    {"label": "CONTAINS_THREAD", "description": "Session -> Message (The first message of the session)."},
    {"label": "NEXT_MESSAGE", "description": "Message -> Message. Maintains the linear flow of chat."},
    
    {"label": "SENT_BY", "description": "Message -> User OR Message -> Agent"},
    
    {"label": "KNOWS_FACT", "description": "User -> Fact. (e.g., User KNOWS_FACT 'Is a Nurse')"},
    {"label": "MENTIONS_ENTITY", "description": "Message -> Entity. (e.g., 'I love Luna' -> Luna)"},
    {"label": "RELATED_TO", "description": "Entity -> Entity. (e.g., Luna RELATED_TO Cat)"},
    
    {"label": "EXTRACTED_FROM", "description": "Fact -> Session. Helps you know WHICH conversation revealed the fact."}
]

PATTERNS = [
    ["User", "HAS_SESSION", "Session"],
    
    ["Session", "CONTAINS_THREAD", "Message"], 
    ["Message", "NEXT_MESSAGE", "Message"],
    
    ["Message", "SENT_BY", "User"],
    ["Message", "SENT_BY", "Agent"],
    
    ["User", "KNOWS_FACT", "Fact"],
    ["Fact", "EXTRACTED_FROM", "Session"], 
    
    ["Message", "MENTIONS_ENTITY", "Entity"],
    ["Entity", "RELATED_TO", "Entity"]
]

GRAPH_SCHEMA = {
    "node_types": NODE_TYPES,
    "relationship_types": RELATIONSHIP_TYPES,
    "patterns": PATTERNS
}










