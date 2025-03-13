from pymongo import MongoClient
import config

client = MongoClient(config.MONGO_URI)
db = client[config.DB_NAME]
collection = db[config.COLLECTION_NAME]

def save_movie_details(movie_data):
    """
    Saves movie details to MongoDB Atlas if not already present.
    """
    existing_movie = collection.find_one({"Title": movie_data["Title"]})
    if not existing_movie:
        collection.insert_one(movie_data)
        print(f"✅ Saved: {movie_data['Title']} to MongoDB")
    else:
        print(f"⚠️ Movie already exists in MongoDB.")

def get_movie_details(movie_title):
    """
    Retrieves movie details from MongoDB Atlas.
    """
    return collection.find_one({"Title": movie_title})
