# Functions
function_code_interpreter = {"type": "code_interpreter"}
function_retrieval = {"type": "retrieval"}

function_record_user_death = {
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
    }
}

function_record_decision = {
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
    }
}

function_display_choices = {
    "type": "function",
    "function": {
        "name": "display_choices",
        "description": "Before User must take a decision, it will have a list of choices to make.",
        "parameters": {
            "type": "object",
            "properties": {
                "choices[]": {
                    "type": "string",
                    "description": "Array of possible Choices for the User",
                }
            },
            "required": ["choices"],
        },
    }
}

# Configs
tools = [
    function_record_decision,
    function_record_user_death
]

tools_init = [
    function_display_choices,
]
