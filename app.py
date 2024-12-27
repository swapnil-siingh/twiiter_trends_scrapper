from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import subprocess
import json
import requests
from datetime import datetime


app = Flask(__name__)

# Set up MongoDB client
client = MongoClient("mongodb://localhost:27017/")
db = client.twitter_scraper
collection = db.trends



def serialize_document(doc):
    """
    Converts MongoDB document's ObjectId to a string for JSON serialization.
    """
    doc["_id"] = str(doc["_id"])
    return doc


@app.route("/", methods=["GET"])
def home():
    """
    Renders the homepage.
    """
    return render_template("index.html")


@app.route("/run_script", methods=["POST"])
def run_script():
    """
    Endpoint to run the scraper script with user credentials.
    """
    try:
        # Get username and password from the request
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username or password missing"}), 400
        
        end_time = datetime.utcnow()
        
        # This ip address when using proxies
        ip_address = requests.get('https://api.ipify.org').text
        print("ip address is this",ip_address)
        # Pass the credentials to the scraper using environment variables
        subprocess.run(
            ["python", "scraper.py", username, password],
            check=True,
        )
        collection.insert_one({
            "trends": [],  # Replace with actual trends
            "timestamp": end_time,  # Store the UTC timestamp
            "ip_address": ip_address,  # Store the IP address
            "unique_id":"unique_id_value"  # Generate unique ID 
        })
        print(" time is this",end_time)
        return jsonify({"message": "Scraper ran successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_data", methods=["GET"])
def get_data():
    """
    Fetch the latest scraped data from MongoDB and return it as JSON.
    """
    try:
        # Fetch the most recent document
        document = collection.find_one(sort=[("timestamp",-1)])
        if document:
            return jsonify(serialize_document(document))
        else:
            return jsonify({"message": "No data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
