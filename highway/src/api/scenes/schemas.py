from pydantic import BaseModel
import base64
import os

from src.models.scene import Scene


class SceneCreate(BaseModel):
    choice_text: str | None = None
    energy_cost: int = 1


class SceneOut(BaseModel):
    id: str
    description: str | None = None
    # Base64 encoded PNG image data (without data URI prefix) to be sent directly to clients
    image_data: str | None = None

    # Deprecated: still present for backward compatibility but will contain None for newly generated scenes
    image_url: str | None = None
    choices_json: dict | None = None

    class Config:
        from_attributes = True

def _encode_image_to_b64(image_path: str | None) -> str | None:
    """Read image file and return base64-encoded string or None if not found."""

    if not image_path:
        return None
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        # In case of any IO errors, fall back to None
        return None
    return None


def scene_to_out(scene: Scene) -> SceneOut:
    """Convert Scene ORM instance to SceneOut schema including image data."""

    return SceneOut(
        id=str(scene.id),
        description=scene.description,
        image_url=None,  # Deprecated – always None for new responses
        image_data=_encode_image_to_b64(scene.image_path),
        choices_json=scene.generated_choices,
    )
