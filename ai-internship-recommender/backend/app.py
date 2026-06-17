import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from recommender import get_recommendations

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "../frontend"),
    static_folder=os.path.join(BASE_DIR, "../frontend/static")
)

CORS(app)

# Landing page
@app.route("/")
def landing():
    return render_template("landing.html")

# App page
@app.route("/app")
def home():
    return render_template("index.html")

# Recommend API
@app.route("/recommend", methods=["POST"])
def recommend():
    data      = request.get_json()
    education = data.get("education", "")
    skills    = data.get("skills", "")
    sector    = data.get("sector", "")
    location  = data.get("location", "")

    if not skills:
        skills = ""

    results = get_recommendations(education, skills, sector, location)

    return jsonify({
        "success": True,
        "count": len(results),
        "recommendations": results
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)