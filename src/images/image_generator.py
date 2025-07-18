from google.genai import types
import os
from PIL import Image
from io import BytesIO
from datetime import datetime
import logging
import asyncio
import gradio as gr
from config import settings
from services.google import GoogleClientFactory
from agent.utils import with_retries

logger = logging.getLogger(__name__)

safety_settings = [
    types.SafetySetting(
        category="HARM_CATEGORY_HARASSMENT",
        threshold="BLOCK_NONE",  # Block none
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_HATE_SPEECH",
        threshold="BLOCK_NONE",  # Block none
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
        threshold="BLOCK_NONE",  # Block none
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="BLOCK_NONE",  # Block none
    ),
]


async def generate_image(prompt: str) -> tuple[str, str] | None:
    """
    Generate an image using Google's Gemini model and save it to generated/images directory.

    Args:
        prompt (str): The text prompt to generate the image from

    Returns:
        str: Path to the generated image file, or None if generation failed
    """
    # Ensure the generated/images directory exists
    output_dir = "generated/images"
    os.makedirs(output_dir, exist_ok=True)

    logger.info(f"Generating image with prompt: {prompt}")

    try:
        async with GoogleClientFactory.image() as client:
            response = await with_retries(
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash-preview-image-generation",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["TEXT", "IMAGE"],
                        safety_settings=safety_settings,
                    ),
                )
            )

        # Process the response parts
        image_saved = False
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                # Create a filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"gemini_{timestamp}.png"
                filepath = os.path.join(output_dir, filename)

                # Save the image
                image = Image.open(BytesIO(part.inline_data.data))
                await asyncio.to_thread(image.save, filepath, "PNG")
                logger.info(f"Image saved to: {filepath}")
                image_saved = True

                return filepath, prompt

        if not image_saved:
            gr.Warning("Image was censored by Google!")
            logger.error("No image was generated in the response.")
            return None, None

    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return None, None


async def modify_image(image_path: str, modification_prompt: str) -> str | None:
    """
    Modify an existing image using Google's Gemini model based on a text prompt.

    Args:
        image_path (str): Path to the existing image file
        modification_prompt (str): The text prompt describing how to modify the image

    Returns:
        str: Path to the modified image file, or None if modification failed
    """
    # Ensure the generated/images directory exists
    output_dir = "generated/images"
    os.makedirs(output_dir, exist_ok=True)

    logger.info(f"Modifying current scene image with prompt: {modification_prompt}")

    # Check if the input image exists
    if not os.path.exists(image_path):
        logger.error(f"Error: Image file not found at {image_path}")
        return None

    try:
        async with GoogleClientFactory.image() as client:
            # Load the input image
            input_image = Image.open(image_path)

            # Make the API call with both text and image
            response = await with_retries(
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash-preview-image-generation",
                    contents=[modification_prompt, input_image],
                    config=types.GenerateContentConfig(
                        response_modalities=["TEXT", "IMAGE"],
                        safety_settings=safety_settings,
                    ),
                ),
            )

        # Process the response parts
        image_saved = False
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                # Create a filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"gemini_modified_{timestamp}.png"
                filepath = os.path.join(output_dir, filename)

                # Save the modified image
                modified_image = Image.open(BytesIO(part.inline_data.data))
                await asyncio.to_thread(modified_image.save, filepath, "PNG")
                logger.info(f"Modified image saved to: {filepath}")
                image_saved = True

                return filepath, modification_prompt

        if not image_saved:
            gr.Warning("Updated image was censored by Google!")
            logger.error("No modified image was generated in the response.")
            return None, None

    except Exception as e:
        logger.error(f"Error modifying image: {e}")
        return None, None


if __name__ == "__main__":
    # Example usage
    sample_prompt = "A Luke Skywalker half height sprite with white background for visual novel game"
    generated_image_path = generate_image(sample_prompt)

    # if generated_image_path:
    #     # Example modification
    #     modification_prompt = "Now the house is destroyed, and the jawas are running away"
    #     modified_image_path = modify_image(generated_image_path, modification_prompt)
    #     if modified_image_path:
    #         print(f"Successfully modified image: {modified_image_path}")
