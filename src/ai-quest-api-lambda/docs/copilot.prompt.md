dev prompt
===

I am building a text-based game that leverages OpenAI capabilities to make AI acts like a dungeon master whereas user can normally choose between proposed actions or come up with own.

# BE logic
API is implemented on AWS lambda in python with fastapi and Mangum for aws lambda compatibility.

I want to have the following API endpoints:
- `POST /api/v1/action` with payload `{"message": "Where am I?", "thread_id": "thread_abcdef"}` to
post User Action to the thread and create a run with Dungeon Master Assistant that will process the User Action
- `GET /api/v1/messages/{threadId}` - to pull all messages from the thread.


# FE logic

## Init
- Initiate a new game with `POST /api/v1/init/` call
    - will create new thread
    - will add basic default user prompt "Hello?" from the User
    - will create a run with DM
    - will return: `thread_id`, `run_id`

## Game cycles
- Post player Decision with `POST /api/v1/action/` call
- get `thread_id`, `run_id` as response
- save `thread_id` locally for future usage
- start polling for run status with `run_id` (https://platform.openai.com/docs/api-reference/runs/getRun)
    - repeat until status is `completed` or return warning `Please, refresh manually` after 10 fails
    - if `status` is `requires_action` and  `required_action.type` is `submit_tool_outputs` -> call `POST /api/v1/run-tools`
- on run success -> pull messages to refresh the story
- wait for User input