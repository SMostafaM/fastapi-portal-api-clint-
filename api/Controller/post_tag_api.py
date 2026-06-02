from fastapi import Header, HTTPException, status, APIRouter, Depends
from bson import ObjectId
import datetime
import jwt

from Model import Post
from core.database import get_db

SECRET_KEY_USERNAME = "0041e6ad98c3ae252d"
ALGORITHM_USERNAME = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES_USERNAME = 5

router = APIRouter()


def get_collections(db):
    return (
        db.post_tag,
        db.log
    )


def convert_mongo_to_json(item):
    if isinstance(item, dict):
        return {k: (str(v) if isinstance(v, ObjectId) else v) for k, v in item.items()}
    return item


def fixid(user):
    user["_id"] = str(user["_id"])
    return user


@router.get("/post/tag/index")
async def index(
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    tag_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        tags = tag_collection.find({})

        tag_list = []
        async for tag in tags:
            tag_list.append(fixid(tag))

        log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "index",
            "subject": "post_tag",
            "object": "0"
        })

        return tag_list

    raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/post/tag/detail/{itemid}")
async def detail(
    itemid: str,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    tag_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        id = ObjectId(itemid)
        tag = await tag_collection.find_one({"_id": id})
        tag = fixid(tag)

        log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "detail",
            "subject": "tag",
            "object": itemid
        })

        return tag

    raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/post/tag/create")
async def create(
    tag: Post.Tag,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    tag_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        await tag_collection.insert_one(tag.dict())

        await log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "create",
            "subject": "tag",
            "object": tag.dict()
        })

        raise HTTPException(status_code=status.HTTP_200_OK, detail="inserted")

    raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)


@router.delete("/post/tag/delete/{itemid}")
async def delete(
    itemid: str,
    Xtoken: str = Header(""),
    Ujtoken: str = Header(""),
    db=Depends(get_db)
):
    tag_collection, log_collection = get_collections(db)

    user_info_token = jwt.decode(Ujtoken, SECRET_KEY_USERNAME, algorithms=[ALGORITHM_USERNAME])
    user_info_token_username = user_info_token["username"]

    if Xtoken == "0041e6ad98c3ae252dcca3f50e82fdf2d57a65fc":

        id = ObjectId(itemid)

        old_item = await tag_collection.find_one({"_id": id})

        await tag_collection.delete_one({"_id": id})

        await log_collection.insert_one({
            "user": user_info_token_username,
            "time": datetime.datetime.now(),
            "action": "delete",
            "subject": "tag",
            "object": old_item
        })

        return HTTPException(detail="deleted", status_code=status.HTTP_200_OK)

    raise HTTPException(detail="bad requst", status_code=status.HTTP_400_BAD_REQUEST)