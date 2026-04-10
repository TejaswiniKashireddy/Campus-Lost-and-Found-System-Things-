"""
backend/models/user_model.py
PyMongo helper functions for the users collection.
"""
from pymongo import MongoClient
from bson import ObjectId

client    = MongoClient("mongodb://localhost:27017")
users_col = client["campus_lnf"]["users"]


def get_user_by_id(user_id):
    return users_col.find_one({"_id": ObjectId(user_id)})


def get_user_by_username(username):
    return users_col.find_one({"username": username})


def get_all_users():
    return list(users_col.find().sort("created_at", -1))
