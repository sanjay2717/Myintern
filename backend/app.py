import os
import sys

# Add backend folder to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from recommender import get_recommendations

# --------------------------------------------------
# Initialize Flask app
# --------------------------------------------------

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "../frontend")
)

CORS(app)

# --------------------------------------------------
# Route - Serve frontend
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")

# --------------------------------------------------
# Route - Get recommendations
# --------------------------------------------------

@app.route("/recommend", methods=["POST"])
def recommend():

    data = request.get_json()

    # Extract inputs with safe defaults
    education = data.get("education", "")
    skills    = data.get("skills", "")
    sector    = data.get("sector", "")
    location  = data.get("location", "")

    # Replace None or missing with empty string
    if not skills:
        skills = ""

    # Get recommendations from engine
    results = get_recommendations(
        education,
        skills,
        sector,
        location
    )

    return jsonify({
        "success": True,
        "count": len(results),
        "recommendations": results
    })

# --------------------------------------------------
# Run server
# --------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)