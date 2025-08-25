import json
import os


class Translator:
    _instances: dict[str, 'Translator'] = {}

    def __init__(self, locale: str):
        self.locale = locale
        self.translations = self._load_translations()

    @classmethod
    def get_instance(cls, locale: str) -> 'Translator':
        """Get or create a Translator instance for the given locale."""
        if locale not in cls._instances:
            cls._instances[locale] = cls(locale)
        return cls._instances[locale]

    def _load_translations(self) -> dict:
        """Load translations from JSON file for the given locale."""
        translations_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'translations',
            f'{self.locale}.json'
        )

        try:
            with open(translations_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback to English if locale file doesn't exist
            if self.locale != 'en':
                fallback_path = os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    'translations',
                    'en.json'
                )
                with open(fallback_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            raise

    def translate(self, key: str) -> str:
        """
        Translate a key using dot notation (e.g., 'chapter_summarization.instruction').
        Falls back to English if translation is not found.
        """
        keys = key.split('.')
        value = self.translations

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            # Fallback to English
            if self.locale != 'en':
                english_translator = Translator.get_instance('en')
                return english_translator.translate(key)
            raise KeyError(f"Translation key '{key}' not found")

