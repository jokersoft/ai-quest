TODO
====

- featureSwitch: function_call.enabled
- messageHistory
  - return by name
  - optimise FE
    - return last N messages on action
- add player name to system prompt
- State:
  - user Name
  - health
  - valuables
  - karma
- set roles https://platform.openai.com/docs/guides/gpt/chat-completions-api
  - function
- function (!!!)
  - multi function: https://community.openai.com/t/emulated-multi-function-calls-within-one-request/269582/13 
  - if response_message.get("function_call"): https://platform.openai.com/docs/guides/gpt/function-calling
  - "Only use the functions you have been provided with."
- authN/authZ
- messages -> embeddings
- split Situations into O,S,C (or not, or denormalize ???)

# Investigations
- temperature

# IDEAS
- role per Situation / Decision / Outcome
  - name them as game Entities
- management simulation game
