I am creating a thin FE app for my backend API (text rpg).


I want to have a few sections:
- dropdown where I can select my current story (list of stories from api call). On dropdown change - load the full story. `GET /stories`. Returns a list of Story objects.
- current full story: big area with the summary of the current story and a list of messages of me vs dungeon master (like chat) `GET /story/{id}` returns the FullStory object.
- Textarea to type and send my actions to the story API (+ button). `POST /story/{story_id}/act` with payload `{ "message": "my action" }`. Returns FullStory. Needs to refresh the current story view.
- button to start a new story (which will call `POST /stories/init` with no payload).
- debug area at the bottom to display responses of all API calls made.

Also:
- use accounts.google.com/gsi/client to authenticate users (client_id=44639786367-9hph0j2ih57oc1a8pbo573jdm7nspsqo.apps.googleusercontent.com)

FullStory response structure:
`GET /story/{id}`:
```json
{
  "status": 200,
  "statusText": "",
  "data": {
    "id": "c703a00a-481d-4ba4-9228-b0252d39c93e",
    "user_id": "e60dfbbd-1b54-4823-99ad-7c02c32d74d7",
    "title": null,
    "messages": [
      {
        "role": "assistant",
        "content": "intro text"
      },
      {
        "role": "user",
        "content": "Hello!"
      }
    ]
  }
}
```

`GET /stories`:
```json
{
  "status": 200,
  "statusText": "",
  "data": [
    {
      "id": "c703a00a-481d-4ba4-9228-b0252d39c93e",
      "user_id": "e60dfbbd-1b54-4823-99ad-7c02c32d74d7",
      "title": "title 1"
    },
    {
      "id": "f367b15a-becb-4fc2-a110-41b4509e570f",
      "user_id": "e60dfbbd-1b54-4823-99ad-7c02c32d74d7",
      "title": "title 2"
    }
  ]
}
```
`POST /stories/init`:
```json
{
  "status": 200,
  "statusText": "",
  "data": {
    "id": "b9412ca2-d092-4843-a619-253fd38dc394",
    "user_id": "e60dfbbd-1b54-4823-99ad-7c02c32d74d7",
    "title": "*The world around you is a desolate wasteland, once a thriving metropolis now reduced to rubble and ruin. The air is thick with the scent of ozone and decay. You stand at the edge of what was once a highway, now cracked and overgrown with strange, luminesc",
    "messages": [
      {
        "role": "user",
        "content": "Hello!"
      },
      {
        "role": "assistant",
        "content": "*The world around you is a desolate wasteland, once a thriving metropolis now reduced to rubble and ruin. The air is thick with the scent of ozone and decay. You stand at the edge of what was once a highway, now cracked and overgrown with strange, luminescent fungi.*\n\nAh, another wanderer in this forsaken hellscape. How... delightful. I'm sure you'll last longer than the last one. Maybe even a whole day.\n\n**Situation:**\nYou notice a faint glow coming from beneath an overturned bus about fifty meters ahead. Beside you is a rusted shopping cart containing a few meager supplies: a half-empty water bottle, a knife with a chipped blade, and a curious amulet that occasionally pulses with a dull blue light.\n\n**Choice:**\n- Investigate the glow beneath the bus\n- Examine the amulet more closely\n- Take the supplies and head in the opposite direction of the bus\n- Try to climb to higher ground for a better view of your surroundings\n\nWhat's your action, survivor?"
      }
    ]
  }
}
```