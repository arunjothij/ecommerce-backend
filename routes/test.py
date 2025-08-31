from pymongo import MongoClient
import certifi
import os
from dotenv import load_dotenv

load_dotenv()
uri = os.getenv("MONGO_URI")

print("Connecting to:", uri)

client = MongoClient(uri, tlsCAFile=certifi.where())
print(client.admin.command("ping"))
