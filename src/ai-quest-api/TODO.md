TODO
====

- Make use of choices of last chapter
  - add choices of the last chapter to the FullStoryResponse.choices?
  - remove choices from each Chapter response
- basic actual test
- Implement long term memory
  - https://www.philschmid.de/gemini-with-memory
- pagination
  - "or meaningful window"
  - wait until we hit limits or produce costs

Story data model:
- short summary (mutable)
- name (mutable)

## Features
- health
  - or "viability" - must end story if runs out 
- valuables (inventory)
- karma (choices/decisions)
- generate book from your adventures
- after 100 messages allow to reflect on choices
- "meaningness" of events (outcomes?)
  - to exclude from the context for low importance
  - to make high importance events shape title and summary
- response streaming via socket or streamlit

## R'n'D
- multiplayer
- management simulation game
