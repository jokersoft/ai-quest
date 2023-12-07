import os


class SituationContentProvider:
    def __init__(self):
        self.situation_to_file_map = {
            "system": "./app/data/prompts/dm.txt",
            "storyteller_message_parser": "./app/data/prompts/storyteller_message_parser.txt",
        }

    def get_content(self, situation: str) -> str:
        file_path = self.situation_to_file_map.get(situation)
        if file_path and os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                return file.read().strip()
        else:
            raise ValueError(f"No file found for situation: {situation} {os.getcwd()}")
