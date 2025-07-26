import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.scene import Scene
from src.models.choice import Choice
import os
import random


async def create_and_store_scene(db: AsyncSession, session_id: uuid.UUID, choice_text: str | None) -> Scene:
    res = await db.execute(select(func.max(Scene.order_num)).where(Scene.session_id == session_id))
    max_order = res.scalar_one()
    order_num = 1 if max_order is None else max_order + 1
    images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "..", "images")
    image_files = [f for f in os.listdir(images_dir) if f.lower().endswith((".jpg", ".png"))]
    image_path = None
    if image_files:
        image_path = os.path.join("images", random.choice(image_files))

    scene = Scene(
        session_id=session_id,
        order_num=order_num,
        description=f"Scene {order_num}",
        image_path=image_path,
    )
    db.add(scene)
    await db.flush()

    if choice_text:
        choice = Choice(scene_id=scene.id, choice_text=choice_text)
        db.add(choice)

    await db.commit()
    await db.refresh(scene)
    return scene
