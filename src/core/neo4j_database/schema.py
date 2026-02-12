# NODE_TYPES = [
#     {"label": "Country", "properties": [{"name": "name", "type": "STRING"}, {"name": "description", "type": "STRING"}]},
#     {"label": "City", "properties": [{"name": "name", "type": "STRING"}, {"name": "description", "type": "STRING"}]},
#     {"label": "Port", "properties": [{"name": "name", "type": "STRING"}, {"name": "description", "type": "STRING"}]},
#     {"label": "Category", "properties": [{"name": "name", "type": "STRING"}, {"name": "description", "type": "STRING"}]},
#     {"label": "Activity", "properties": [{"name": "name", "type": "STRING"}, {"name": "description", "type": "STRING"}]},
#     {"label": "Cuisine", "properties": [{"name": "name", "type": "STRING"}, {"name": "description", "type": "STRING"}]},
#     {"label": "Shopping", "properties": [{"name": "name", "type": "STRING"}, {"name": "description", "type": "STRING"}]},
#     {"label": "Museum", "properties": [{"name": "name", "type": "STRING"}, {"name": "description", "type": "STRING"}]},
#     {"label": "HistoricalSite", "properties": [{"name": "name", "type": "STRING"}, {"name": "description", "type": "STRING"}]},
#     {"label": "InsiderTip", "properties": [{"name": "name", "type": "STRING"}, {"name": "description", "type": "STRING"}]}
# ]

# RELATIONSHIP_TYPES = [
#     {"label": "IS_CITY_OF"},
#     {"label": "HAS_PORT"},
#     {"label": "HAS_CATEGORY"},       # Port -> Category
#     {"label": "INCLUDES_ITEM"},      # Category -> (Activity, Museum, etc.)
#     {"label": "HAS_INSIDER_TIP"}     # (Activity/Cuisine/etc.) -> InsiderTip
# ]

# PATTERNS = [
#     ["City", "IS_CITY_OF", "Country"],    
#     ["City", "HAS_PORT", "Port"],        
    
#     # Tier 1: Port to Categories
#     ["Port", "HAS_CATEGORY", "Category"], 
    
#     # Tier 2: Categories to specific Features
#     ["Category", "INCLUDES_ITEM", "Activity"],
#     ["Category", "INCLUDES_ITEM", "Museum"],
#     ["Category", "INCLUDES_ITEM", "HistoricalSite"],
#     ["Category", "INCLUDES_ITEM", "Shopping"],
#     ["Category", "INCLUDES_ITEM", "Cuisine"],

#     # Tier 3: Contextual Tips (Connected to the item, not the port)
#     ["Activity", "HAS_INSIDER_TIP", "InsiderTip"],
#     ["Museum", "HAS_INSIDER_TIP", "InsiderTip"],
#     ["HistoricalSite", "HAS_INSIDER_TIP", "InsiderTip"],
#     ["Shopping", "HAS_INSIDER_TIP", "InsiderTip"],
#     ["Cuisine", "HAS_INSIDER_TIP", "InsiderTip"]
# ]

# GRAPH_SCHEMA = {
#     "node_types": NODE_TYPES,
#     "relationship_types": RELATIONSHIP_TYPES,
#     "patterns": PATTERNS
# }
# 

NODE_TYPES = [
    # --- Geographic & Destination Nodes ---
    {
        "label": "Destination", 
        "properties": [
            {"name": "name", "type": "STRING", "description": "e.g., Perfect Day at CocoCay"},
            {"name": "description", "type": "STRING"},
            {"name": "avg_rating", "type": "FLOAT"},
            {"name": "review_count", "type": "INTEGER"}
        ]
    },
    {
        "label": "Zone", 
        "properties": [
            {"name": "name", "type": "STRING", "description": "e.g., Thrill Waterpark, Chill Island, South Beach"},
            {"name": "description", "type": "STRING"},
            {"name": "tagline", "type": "STRING", "description": "e.g., 'Cranked up thrills'"},
            {"name": "video_url", "type": "STRING"},
            {"name": "is_exclusive", "type": "BOOLEAN", "description": "True for Coco Beach Club / Hideaway Beach"}
        ]
    },
    {
        "label": "Venue", 
        "properties": [
            {"name": "name", "type": "STRING", "description": "e.g., Daredevil's Peak, Skipper's Grill"},
            {"name": "type", "type": "STRING", "description": "e.g., Slide, Pool, Restaurant, Bar, Cabana"},
            {"name": "description", "type": "STRING"},
            {"name": "thrill_level", "type": "STRING", "description": "e.g., 'Mild', 'Strenuous'"},
            {"name": "is_complimentary", "type": "BOOLEAN", "description": "True if included in fare, False if upcharge"},
            {"name": "water_depth", "type": "STRING"},
            {"name": "opening_hours", "type": "STRING"}
        ]
    },
    {
        "label": "LogisticsPoint",
        "properties": [
            {"name": "name", "type": "STRING", "description": "e.g., Breezy Bay Tram Stop, Arrivals Plaza"},
            {"name": "type", "type": "STRING", "description": "Tram Stop, Bathroom, Towel Station, Locker Area"}
        ]
    },

    # --- Cruise & Itinerary Nodes ---
    {
        "label": "Ship", 
        "properties": [
            {"name": "name", "type": "STRING", "description": "e.g., Icon of the Seas"},
            {"name": "class", "type": "STRING", "description": "e.g., Icon Class, Oasis Class"},
            {"name": "guest_capacity", "type": "INTEGER"}
        ]
    },
    {
        "label": "Itinerary", 
        "properties": [
            {"name": "name", "type": "STRING", "description": "e.g., 7 Night Western Caribbean & Perfect Day"},
            {"name": "duration_nights", "type": "INTEGER"},
            {"name": "embarkation_port", "type": "STRING"}
        ]
    },
    {
        "label": "Sailing",
        "properties": [
            {"name": "departure_date", "type": "DATE"},
            {"name": "price_lowest", "type": "FLOAT"},
            {"name": "price_currency", "type": "STRING"}
        ]
    },

    # --- Rule & Requirement Nodes ---
    {
        "label": "Restriction", 
        "properties": [
            {"name": "min_height_inches", "type": "INTEGER"},
            {"name": "max_weight_lbs", "type": "INTEGER"},
            {"name": "min_age_years", "type": "INTEGER"},
            {"name": "description", "type": "STRING", "description": "Full text like '48 inches minimum'"}
        ]
    },
    {
        "label": "Pass", 
        "properties": [
            {"name": "name", "type": "STRING", "description": "e.g., Thrill Waterpark Full Day Pass"},
            {"name": "category", "type": "STRING", "description": "Shore Excursion, Day Pass"},
            {"name": "dynamic_price_min", "type": "FLOAT", "description": "Lowest observed price"},
            {"name": "dynamic_price_max", "type": "FLOAT", "description": "Highest observed price"}
        ]
    }
]

RELATIONSHIP_TYPES = [
    # Spatial / Hierarchy
    {"label": "HAS_ZONE", "description": "Destination contains a major neighborhood"},
    {"label": "CONTAINS_VENUE", "description": "Zone contains a specific attraction/restaurant"},
    {"label": "LOCATED_NEAR", "description": "Navigational adjacency (e.g., 'Also close by')"},
    {"label": "SERVED_BY_TRAM", "description": "Zone connects to a specific tram stop"},
    
    # Requirements & Rules
    {"label": "HAS_RESTRICTION", "description": "Venue enforces specific height/weight rules"},
    {"label": "REQUIRES_PASS", "description": "Venue requires a specific purchased pass to enter"},
    
    # Logistics
    {"label": "HAS_NEAREST_BATHROOM", "description": "Navigation helper scraped from 'Location and getting here'"},
    {"label": "HAS_NEAREST_DINING", "description": "Navigation helper scraped from 'Location and getting here'"},

    # Cruise Operation
    {"label": "SAILS_ITINERARY", "description": "Ship performs a specific route"},
    {"label": "VISITS_DESTINATION", "description": "Itinerary includes a stop at this place"},
    {"label": "HAS_SAILING", "description": "Itinerary has a specific departure date instance"}
]

PATTERNS = [
    # Hierarchy Mapping
    ["Destination", "HAS_ZONE", "Zone"],
    ["Zone", "CONTAINS_VENUE", "Venue"],
    ["Zone", "LOCATED_NEAR", "Zone"],
    
    # Logistics Mapping (from 'Location and getting here' section)
    ["Zone", "SERVED_BY_TRAM", "LogisticsPoint"],
    ["Zone", "HAS_NEAREST_BATHROOM", "LogisticsPoint"], 
    ["Venue", "HAS_NEAREST_DINING", "Venue"],
    
    # Restriction Mapping (from 'Restrictions' section)
    ["Venue", "HAS_RESTRICTION", "Restriction"],
    ["Zone", "HAS_RESTRICTION", "Restriction"], # e.g., Hideaway Beach is 18+
    
    # Commercial/Booking Mapping
    ["Venue", "REQUIRES_PASS", "Pass"], # e.g., Thrill Waterpark Slides -> Thrill Waterpark Pass
    
    # Cruise Mapping
    ["Ship", "SAILS_ITINERARY", "Itinerary"],
    ["Itinerary", "VISITS_DESTINATION", "Destination"],
    ["Itinerary", "HAS_SAILING", "Sailing"]
]

GRAPH_SCHEMA = {
    "node_types": NODE_TYPES,
    "relationship_types": RELATIONSHIP_TYPES,
    "patterns": PATTERNS,
    "additional_node_types": True,
    "additional_relationship_types": True,
    "additional_patterns": True
}










