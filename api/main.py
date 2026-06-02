from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
from Controller import (
    login_api,
    sinup_api,
    send_sms,
    user_api,
    notif_api,
    post_tag_api,
    post_api,
    search_api,
    form_group_api,
    form_api,
    index_api,
    interaction_api,
)
# from Controller import send_sms
# from Controller import user_api
# from Controller import notif_api
import os
import uvicorn
from core.database import startup_db, shutdown_db


@asynccontextmanager
async def lifespan(app: FastAPI):

    client, db = await startup_db()

    app.state.client = client
    app.state.db = db

    yield

    await shutdown_db(client)



app = FastAPI(lifespan=lifespan)
# اضافه کردن router کنترلر جدید به اپلیکیشن
app.include_router(login_api.router)
app.include_router(sinup_api.router)
app.include_router(send_sms.router)
app.include_router(user_api.router)
app.include_router(notif_api.router)
app.include_router(post_tag_api.router)
app.include_router(form_group_api.router)
app.include_router(index_api.router)
app.include_router(interaction_api.router)
app.include_router(post_api.router)
app.include_router(form_api.router)
app.include_router(search_api.router)



# @app.on_event("startup")
# async def startup_event():
#     client = AsyncIOMotorClient('mongodb://localhost:27017')
#     db = client.portal

#     await client.admin.command('ping')
#     print("✅ Successfully connected to MongoDB!")

#     app.state.client = client
#     app.state.db = db

#     post_collection = db.get_collection("post")
#     await post_collection.create_index("create_at",expireAfterSeconds=30*24*60*60)


# async def shutdown_event():
#     # بستن اتصال دیتابیس هنگام خاموش شدن برنامه
#     app.state.client.close()
#     print("🔌 MongoDB connection closed.")

    


# @app.get("/")
# async def root():
#     return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001)