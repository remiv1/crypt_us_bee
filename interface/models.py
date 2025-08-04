from typing import Optional
from pymongo import MongoClient
import sqlite3
from typing import Any
from os import getenv

client: Optional[MongoClient[Any]] = None
conn: Optional[sqlite3.Connection] = None

if getenv("ENV") == "production":
    # Configuration MongoDB
    client = MongoClient("mongodb://mongo:27017/")
    db = client["encripted_db"]
else:
    # Configuration SQLite
    conn = sqlite3.connect("development.db")