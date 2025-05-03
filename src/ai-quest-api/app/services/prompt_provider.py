import os
import sys


class PromptProvider:
    def __init__(self):
        app_root_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.directory_path = f"{app_root_folder}/static/prompts"

    def get(self, prompt_name):
        file_path = os.path.join(self.directory_path, f"{prompt_name}.txt")
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return f"Prompt '{prompt_name}' not found."
