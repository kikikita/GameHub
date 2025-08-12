from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.mongo import MongoStorage
from motor.motor_asyncio import AsyncIOMotorClient
from settings import settings

bot_instance = Bot(token=settings.bots.bot_token.get_secret_value())

# Mongo-backed FSM storage for aiogram
mongo_client = AsyncIOMotorClient(settings.bots.mongo_uri)
storage = MongoStorage(client=mongo_client, db_name=settings.bots.mongo_db, collection_name=settings.bots.mongo_collection)

dp_instance = Dispatcher(storage=storage)