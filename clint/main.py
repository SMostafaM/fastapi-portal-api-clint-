from fastapi import FastAPI,Request
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
from Controller import login,sinup,user,notif,post_tag,index,interaction,post,user_self,search,form_group,form
import os
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import jwt
import uvicorn
import asyncio




app = FastAPI()

# اضافه کردن router کنترلر جدید به اپلیکیشن
app.include_router(login.router)
app.include_router(sinup.router)
app.include_router(user.router)
app.include_router(notif.router)
app.include_router(post.router)
app.include_router(form.router)
app.include_router(post_tag.router)
app.include_router(form_group.router)
app.include_router(index.router)
app.include_router(interaction.router)
app.include_router(user_self.router)
app.include_router(search.router)

# Mount the 'static' directory to the '/static' URL path
app.mount("/static", StaticFiles(directory="static"), name="static")


template=Jinja2Templates(directory="templates")



@app.get("/i")
async def root():
    return {"message": "Hello"}

if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0",port=80,reload=False,workers=5)

@app.on_event("startup")
async def startup_ev():
    app.state.semaphore=asyncio.Semaphore(15)

