tools = [
    {
        "type": "function",
        "function": {
            "name": "record_user_death",
            "description": "When conditions are such as when Outcome leads to user death.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Verbose description of the reason of User death ",
                    }
                },
                "required": ["reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_decision",
            "description": "When User takes a decision, it must be recorded with this function",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Verbose description of the Decision the User took",
                    }
                },
                "required": ["description"],
            },
        },
    }
]

# tools=[{"type": "code_interpreter"}, {"type": "retrieval"}]
        