import json
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── LOAD DATA ─────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "internships.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    internships = json.load(f)

# ── BUILD TEXT ────────────────────────────────
def build_internship_text(internship):
    location_boost = (internship["location"] + " ") * 3
    sector_boost   = (internship["sector"]   + " ") * 3
    edu_boost      = (internship["education_required"] + " ") * 2

    return (
        internship["title"]            + " " +
        sector_boost                   +
        location_boost                 +
        edu_boost                      +
        internship["skills_required"]  + " " +
        internship["description"]
    )

internship_texts = [
    build_internship_text(i) for i in internships
]

# ── TF-IDF ────────────────────────────────────
vectorizer        = TfidfVectorizer(stop_words="english")
internship_matrix = vectorizer.fit_transform(internship_texts)

# ── STATE ALIASES ─────────────────────────────
STATE_ALIASES = {
    "Tamil Nadu"      : ["Tamil Nadu", "TN", "Chennai"],
    "Maharashtra"     : ["Maharashtra", "Mumbai", "Pune"],
    "Karnataka"       : ["Karnataka", "Bangalore", "Bengaluru"],
    "Delhi"           : ["Delhi", "New Delhi", "NCR"],
    "Uttar Pradesh"   : ["Uttar Pradesh", "UP", "Lucknow"],
    "West Bengal"     : ["West Bengal", "Kolkata", "WB"],
    "Telangana"       : ["Telangana", "Hyderabad"],
    "Rajasthan"       : ["Rajasthan", "Jaipur"],
    "Madhya Pradesh"  : ["Madhya Pradesh", "MP", "Bhopal"],
    "Bihar"           : ["Bihar", "Patna"],
    "Punjab"          : ["Punjab", "Chandigarh"],
    "Odisha"          : ["Odisha", "Bhubaneswar"],
    "Gujarat"         : ["Gujarat", "Ahmedabad"],
    "Andhra Pradesh"  : ["Andhra Pradesh", "AP", "Vizag"],
    "Haryana"         : ["Haryana", "Gurugram"],
    "Kerala"          : ["Kerala", "Kochi"],
    "Jharkhand"       : ["Jharkhand", "Ranchi"],
    "Chhattisgarh"    : ["Chhattisgarh", "Raipur"],
    "Uttarakhand"     : ["Uttarakhand", "Dehradun"],
    "Himachal Pradesh": ["Himachal Pradesh", "Shimla"]
}

# ── EDUCATION LEVELS ──────────────────────────
EDU_LEVELS = {
    "Class 10"     : 1,
    "Class 12"     : 2,
    "Diploma"      : 3,
    "Graduate"     : 4,
    "Post Graduate": 5
}

# ── BONUS FUNCTIONS ───────────────────────────

def location_bonus(internship_location, user_location):
    if not user_location:
        return 0.0

    user_lower   = user_location.lower().strip()
    intern_lower = internship_location.lower().strip()

    if user_lower == intern_lower:
        return 0.45

    aliases = STATE_ALIASES.get(user_location, [])
    for alias in aliases:
        if alias.lower() in intern_lower:
            return 0.40

    return 0.0

def education_bonus(internship_edu, user_edu):
    if not user_edu or not internship_edu:
        return 0.0

    user_level   = EDU_LEVELS.get(user_edu, 0)
    intern_level = EDU_LEVELS.get(internship_edu, 0)

    if user_level >= intern_level:
        return 0.15
    else:
        return -0.20

def sector_bonus(internship_sector, user_sector):
    if not user_sector:
        return 0.0

    if internship_sector.lower() == user_sector.lower():
        return 0.30

    return 0.0

# ── MAIN FUNCTION ─────────────────────────────

def get_recommendations(education, skills, sector, location):

    location_str = (location  + " ") * 4 if location  else ""
    sector_str   = (sector    + " ") * 4 if sector    else ""
    edu_str      = (education + " ") * 2 if education else ""

    query = (
        edu_str      +
        skills       + " " +
        sector_str   +
        location_str
    ).strip()

    if not query:
        query = "internship india general"

    # TF-IDF similarity scores
    query_vector = vectorizer.transform([query])
    tfidf_scores = cosine_similarity(
        query_vector,
        internship_matrix
    ).flatten()

    # Combined scoring
    final_scores = []

    for i, internship in enumerate(internships):
        tfidf = float(tfidf_scores[i])
        loc_b = location_bonus(internship["location"], location)
        edu_b = education_bonus(internship["education_required"], education)
        sec_b = sector_bonus(internship["sector"], sector)

        final = (tfidf * 0.40) + loc_b + edu_b + sec_b
        final_scores.append((i, final))

    # Sort descending
    final_scores.sort(key=lambda x: x[1], reverse=True)

    # Build top 5 results
    results = []

    for rank, (index, score) in enumerate(final_scores[:5]):
        internship   = internships[index].copy()
        pct          = round(min(score * 100, 99))

        if pct < 30:
            pct = max(30 + (5 - rank) * 4, 30)

        internship["match_score"] = pct
        results.append(internship)

    return results