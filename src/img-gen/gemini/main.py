import dotenv
import os
import google.generativeai as genai

dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# List available models
available_models = genai.list_models()
print("Available models:")
for model in available_models:
    print(model.name)

imagen = genai.ImageGenerationModel("imagen-3.0-generate-001")

result = imagen.generate_images(
    prompt="Unicorns of the Apocalypse",
    number_of_images=2,
    safety_filter_level="block_only_high",
    person_generation="allow_adult",
    aspect_ratio="3:4",
    negative_prompt="anime",
)

for image in result.images:
  print(image)

# Open and display the image using your local operating system.
for image in result.images:
  image._pil_image.show()
