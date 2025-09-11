import logging
import vertexai
import base64
import json
import asyncio
from typing import Optional
from io import BytesIO

from vertexai.generative_models import GenerativeModel
from vertexai.vision_models import ImageGenerationModel

# Assuming config/settings.py contains a `settings` object
from config.settings import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """
    A service class to interact with Google's Gemini and Imagen models.
    """

    def __init__(self):
        print("GeminiService: Initializing...")
        """Initializes the Vertex AI models."""
        try:
            vertexai.init(project=settings.PROJECT_ID, location=settings.LOCATION)
            self.gemini_model = GenerativeModel(settings.GEMINI_MODEL_NAME)
            self.imagen_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")
            logger.info(
                f"GeminiService initialized with models: {settings.GEMINI_MODEL_NAME}, imagen-3.0-generate-002"
            )
        except Exception as e:
            logger.error(
                "---!!! GEMINI SERVICE INITIALIZATION FAILED !!!---", exc_info=True
            )
            self.gemini_model = None
            self.imagen_model = None

    async def generate_text(self, prompt: str, temperature: float = 0.4) -> Optional[str]:
        print(f"GeminiService: generate_text called with prompt length {len(prompt)}")
        print(f"GeminiService: Full prompt being sent to Gemini:\n---\n{prompt}\n---")
        """
        Generates text using the configured Gemini model.

        Returns:
            The generated text string, or a fallback JSON string if generation fails.
        """
        if self.gemini_model is None:
            logger.warning("GeminiService (text model) is not initialized. Cannot generate text.")
            return None

        try:
            response = await self.gemini_model.generate_content_async(
                prompt,
                generation_config={"temperature": temperature},
            )
            print(f"GeminiService: Raw response object from Gemini: {response}")
            generated_text = response.text
            # Clean the response to remove markdown backticks
            cleaned_text = generated_text.strip().replace('```json', '').replace('```', '')
            return cleaned_text
        except Exception as e:
            logger.error(
                f"Error calling Gemini Text API for prompt '{prompt[:100]}...'",
                exc_info=True,
            )
            logger.warning("Falling back to generic JSON response due to Gemini API error.")
            fallback_json_data = {
                "project_charter": {
                    "project_name": "Fallback Project",
                    "client_name": "Fallback Client",
                    "project_description": "This is a fallback project due to API issues.",
                    "project_type": "residential",
                    "budget_range": "$1M - $2M",
                    "location": "Fallback City, Fallback Country",
                },
                "constraints": {
                    "desired_features": ["Fallback Feature 1", "Fallback Feature 2"],
                    "other_limitations": "API access issues",
                },
            }
            fallback_json_string = json.dumps(fallback_json_data, indent=4)
            logger.info(f"Gemini Fallback JSON string: {fallback_json_string}")
            return fallback_json_string

    async def generate_image(self, prompt: str) -> Optional[str]:
        """
        Generates an image from a text prompt using the Imagen model.

        Returns:
            Base64 encoded image string, or a fallback base64 string if generation fails.
        """
        if self.imagen_model is None:
            logger.warning("GeminiService (image model) is not initialized. Cannot generate image.")
            return None

        try:
            logger.info(f"Calling Imagen for prompt: {prompt[:100]}...")
            images = self.imagen_model.generate_images(
                prompt=prompt, number_of_images=1
            )
            if images.images and len(images.images) > 0:
                pil_image = images.images[0]._pil_image
                buffered = BytesIO()
                await asyncio.to_thread(pil_image.save, buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                logger.info("Imagen image generation successful.")
                return img_str
            else:
                logger.warning("Imagen image generation response missing image.")
                return None
        except Exception as e:
            print(f"DEBUG: Exception in generate_image: {e}") # Added for debugging
            import traceback
            traceback.print_exc() # Added for debugging
            logger.error(
                f"Error generating image with Imagen for prompt '{prompt[:100]}...'",
                exc_info=True,
            )
            logger.warning("Falling back to generic image due to Imagen API error.")
            # Fallback to a small transparent PNG base64 string
            return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
