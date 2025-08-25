import os


class PromptProvider:
    def __init__(self, locale='en'):
        app_root_folder = os.path.dirname(os.path.abspath(__file__))
        self.directory_path = os.path.join(app_root_folder, f"../static/prompts/{locale}")

    def get(self, prompt_name):
        file_path = os.path.join(self.directory_path, f"{prompt_name}.txt")
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return f"Prompt '{prompt_name}' not found in {self.directory_path}."
