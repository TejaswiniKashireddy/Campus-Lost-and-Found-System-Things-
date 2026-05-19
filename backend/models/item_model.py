"""
backend/models/item_model.py
PyMongo helper functions for the items collection.
"""
from pymongo import MongoClient
from bson import ObjectId

client    = MongoClient("mongodb://localhost:27017")
items_col = client["campus_lnf"]["items"]


def get_item_by_id(item_id):
    return items_col.find_one({"_id": ObjectId(item_id)})


def get_items_by_type(item_type, limit=12):
    return list(items_col.find({"type": item_type}).sort("created_at", -1).limit(limit))


def get_items_by_user(user_id):
    return list(items_col.find({"user_id": ObjectId(user_id)}).sort("created_at", -1))


def search_items(query="", location=""):
    q = {}
    if query:    q["title"]    = {"$regex": query,    "$options": "i"}
    if location: q["location"] = {"$regex": location, "$options": "i"}
    return list(items_col.find(q).sort("created_at", -1))
