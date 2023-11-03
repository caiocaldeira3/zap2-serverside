import config
from app.models.user import OPKey, User
from app.util import mongodb
from app.util.exc import UserNotFound
from bson import ObjectId


def find_with_telephone (tel: str) -> User:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    result = mdb.find_one({ "telephone": tel })
    if result is None:
        raise UserNotFound

    result["opkeys"] = [ OPKey(**key) for key in result.get("opkeys", ()) ]

    return User(**result)

def find_with_id (user_id: str) -> User:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    result = mdb.find_one({ "_id": user_id })
    if result is None:
        raise UserNotFound

    result["opkeys"] = [ OPKey(**key) for key in result.get("opkeys", ()) ]

    return User(**result)

def find_many (tels: list[str]) -> User:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    return [
        User(**result)
        for result in mdb.find_many({ "telephone": {"$in": tels} })
    ]

def find_connected_users () -> list[User]:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    return [
        User(**result)
        for result in mdb.find_many({ "socket_id": {"$ne": None} })
    ]

def insert_user (user: User) -> None:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    mdb.insert_one(user.to_insert())

def delete_device (socket_id: str) -> bool:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    return mdb.update_one(
        filter={ "socket_id": socket_id },
        update_data={ "$set": { "socket_id": None }}
    )

def disconect_users () -> None:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    return mdb.update_one(
        filter={ "socket_id": {"$ne": None} },
        update_data={ "$set": { "socket_id": None }}
    )


def add_user_device (user_id: ObjectId, socket_id: str) -> bool:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    return mdb.update_one(
        filter={ "_id": user_id },
        update_data={ "$set": { "socket_id": socket_id }}
    )

def init_server_db () -> None:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    mdb.drop_collection()
    mdb.create_index_keys(("telephone", "socket_id"), (True, None))
