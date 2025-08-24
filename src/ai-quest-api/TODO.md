TODO
====

- count tokens used
- tune context
  - messages
  - summarization
  - dialogue continuity
- end_story(death)
  - is_story_over: bool
- basic actual test
- Implement long term memory
  - https://www.philschmid.de/gemini-with-memory
  - s3 for vector storage
    - https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-opensearch.html#s3-vectors-opensearch-engine (cheap option)
  - embedding process
    - https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-bedrock-kb.html
  - https://aws.amazon.com/blogs/aws/introducing-amazon-s3-vectors-first-cloud-storage-with-native-vector-support-at-scale/


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
