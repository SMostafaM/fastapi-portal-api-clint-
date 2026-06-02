from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient


async def startup_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")

    await client.admin.command("ping")
    print("✅ Successfully connected to MongoDB!")

    db = client.portal

    post_collection = db.get_collection("post")

    await post_collection.create_index(
        "create_at",
        expireAfterSeconds=30 * 24 * 60 * 60
    )

    return client, db


async def shutdown_db(client):
    client.close()
    print("🔌 MongoDB connection closed.")


def get_db(request: Request):
    return request.app.state.db