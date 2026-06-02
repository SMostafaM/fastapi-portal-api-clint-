from fastapi import FastAPI, Header, HTTPException, status, Body, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
import os
from Model import Sinup
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import datetime
import jwt
import jdatetime
from core.database import get_db


# کلید مخفی برای ارسال نام کاربری در هدر درخواست ها
SECRET_KEY_USERNAME = "0041e6ad98c3ae252d"
ALGORITHM_USERNAME = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES_USERNAME = 5

# ایجاد یک router جدید
router = APIRouter()


def get_collections(db):
    return (
        db.Users,
        db.form,
        db.form_removed,
        db.sinup,
        db.sinup_removed,
        db.log,
        db.member
    )


def fixid(user):
    user["_id"] = str(user["_id"])
    return user


@router.get("/form/index/{type_user}")
async def index(
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    type_user: str = "0",
    db=Depends(get_db)
):

    User_collection, form_collection, form_collection_rm, sinup_collection, sinup_collection_rm, log_collection, member_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        if type_user == "0":
            forms = form_collection.find({}).sort("_id", -1)
        else:
            forms = form_collection.find({"moavenat": type_user}).sort("_id", -1)

        forms_list = []
        async for form in forms:
            form = fixid(form)
            count_person = await sinup_collection.count_documents({"form_id": form["_id"]})
            form["count_person"] = count_person
            forms_list.append(form)

        log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "index",
            "subject": "form",
            "object": type_user
        })

        return forms_list

    raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/form/detail/{itemid}")
async def detail(
    itemid: str,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):

    User_collection, form_collection, form_collection_rm, sinup_collection, sinup_collection_rm, log_collection, member_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        form = await form_collection.find_one({"_id": ObjectId(itemid)})
        form = fixid(form)

        log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "detail",
            "subject": "form",
            "object": itemid
        })

        return form

    raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/form/show/{itemid}")
async def show(
    itemid: str,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):

    User_collection, form_collection, form_collection_rm, sinup_collection, sinup_collection_rm, log_collection, member_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        id = ObjectId(itemid)
        forms = form_collection.find({"_id": id}, {"show": 1}).sort("_id", -1)

        async for form in forms:
            if form["show"] is True:
                form_collection.update_one({"_id": form["_id"]}, {"$set": {"show": False}})
                log_collection.insert_one({
                    "user": user_info_token_username,
                    "time": datetime.datetime.now(),
                    "action": "False",
                    "subject": "form",
                    "object": itemid
                })
            else:
                form_collection.update_one({"_id": form["_id"]}, {"$set": {"show": True}})
                log_collection.insert_one({
                    "user": user_info_token_username,
                    "time": datetime.datetime.now(),
                    "action": "True",
                    "subject": "form",
                    "object": itemid
                })

        raise HTTPException(status_code=status.HTTP_200_OK, detail="changed")

    raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/form/create")
async def create(
    from_data: Sinup.FormCreate_insert,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):

    User_collection, form_collection, form_collection_rm, sinup_collection, sinup_collection_rm, log_collection, member_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        n_dict = from_data.dict()

        now_shamsi = jdatetime.datetime.now()
        n_dict["date"] = now_shamsi.strftime("%Y-%m-%d %H:%M")

        n_dict["fields"].append({
            "label": "نام کاربری",
            "type": "text",
            "required": True,
            "options": None
        })

        await form_collection.insert_one(n_dict)

        log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "craete",
            "subject": "form",
            "object": n_dict
        })

        raise HTTPException(status_code=status.HTTP_200_OK, detail="inserted")

    raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/form/edite")
async def edite(
    from_data: Sinup.FormCreate,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):

    User_collection, form_collection, form_collection_rm, sinup_collection, sinup_collection_rm, log_collection, member_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        old_item = await form_collection.find_one({"_id": ObjectId(from_data.id)})

        form_d = from_data.dict()
        form_d["_id"] = ObjectId(form_d["id"])
        del form_d["id"]

        await form_collection.delete_one({"_id": ObjectId(from_data.id)})

        now_shamsi = jdatetime.datetime.now()
        form_d["date"] = now_shamsi.strftime("%Y-%m-%d %H:%M")

        await form_collection.insert_one(form_d)

        await log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "edite_form",
            "subject": from_data.dict(),
            "object": old_item
        })

        raise HTTPException(status_code=status.HTTP_200_OK, detail="edited")

    raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.delete("/form/delete/{itemid}")
async def delete(
    itemid: str,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):

    User_collection, form_collection, form_collection_rm, sinup_collection, sinup_collection_rm, log_collection, member_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        id = ObjectId(itemid)

        old_item = await form_collection.find_one({"_id": id})
        await form_collection.delete_one({"_id": id})

        await form_collection_rm.insert_one(old_item)

        sinup_perv = sinup_collection.find({"form_id": itemid})
        await sinup_collection_rm.insert_many(sinup_perv)
        await sinup_collection.delete_many({"form_id": itemid})

        log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "delete",
            "subject": "form",
            "object": old_item
        })

        return HTTPException(detail="deleted", status_code=status.HTTP_200_OK)

    raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.delete("/member/delete/{itemid}")
async def member_delete(
    itemid: str,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):

    User_collection, form_collection, form_collection_rm, sinup_collection, sinup_collection_rm, log_collection, member_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        id = ObjectId(itemid)

        old_item = await sinup_collection.find_one({"_id": id})
        await sinup_collection.delete_one({"_id": id})

        await sinup_collection_rm.insert_one(old_item)

        log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "delete",
            "subject": "sinup",
            "object": old_item
        })

        return HTTPException(detail="deleted", status_code=status.HTTP_200_OK)

    raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)