import os

class SituationContentProvider:
    def __init__(self):
        self.situation_to_file_map = {
            "system": "./app/data/prompts/system.txt",
        }

    def get_content(self, situation: str) -> str:
        file_path = self.situation_to_file_map.get(situation)
        if not file_path or not os.path.isfile(file_path):
            raise ValueError(f"No file found for situation: {situation} {os.getcwd()}")
        with open(file_path, 'r') as file:
            return file.read().strip()
