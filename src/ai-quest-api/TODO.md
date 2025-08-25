TODO
====

- end_story(death)
  - is_story_over: bool
- tune context
  - messages
  - summarization
  - dialogue continuity
- basic actual test

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
- image generation

## R'n'D
- multiplayer
  - play together
  - intersect stories (global memory scope)
- management simulation game
