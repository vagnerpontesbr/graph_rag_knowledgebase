from __future__ import annotations

from pymongo import MongoClient


def get_client(uri: str) -> MongoClient:
    if not uri:
        raise ValueError("MONGODB_URI is required")
    return MongoClient(uri)
