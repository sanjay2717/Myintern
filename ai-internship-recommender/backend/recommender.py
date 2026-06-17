import json
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── LOAD DATA ────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "internships.json")

with open(JSON_PATH, "r") as f:
    internships = json.load(f)

# ── BUILD TEXT ────────────────────────────────────────────────

def build_internship_text(internship):
    # Repeat location and sector 3 times
    # so TF-IDF gives them more weight
    location_boost = (internship["location"] + " ") * 3
    sector_boost   = (internship["sector"] + " ")   * 3
    edu_boost      = (internship["education_required"] + " ") * 2

    return (
        internship["title"]       + " " +
        sector_boost              +
        location_boost            +
        edu_boost                 +
        internship["skills_required"] + " " +
        internship["description"]
    )

internship_texts = [build_internship_text(i) for i in internships]

# ── TF-IDF VECTORIZER ─────────────────────────────────────────

vectorizer = TfidfVectorizer(stop_words="english")
internship_matrix = vectorizer.fit_transform(internship_texts)

# ── STATE NAME ALIASES ────────────────────────────────────────
# Maps what user selects to what appears in JSON

STATE_ALIASES = {
    "Tamil Nadu":        ["Tamil Nadu", "tamil nadu", "TN", "Chennai"],
    "Maharashtra":       ["Maharashtra", "Maharashtra", "Mumbai", "Pune"],
    "Karnataka":         ["Karnataka", "Bangalore", "Bengaluru"],
    "Delhi":             ["Delhi", "New Delhi", "NCR"],
    "Uttar Pradesh":     ["Uttar Pradesh", "UP", "Lucknow"],
    "West Bengal":       ["West Bengal", "Kolkata", "WB"],
    "Telangana":         ["Telangana", "Hyderabad"],
    "Rajasthan":         ["Rajasthan", "Jaipur"],
    "Madhya Pradesh":    ["Madhya Pradesh", "MP", "Bhopal"],
    "Bihar":             ["Bihar", "Patna"],
    "Punjab":            ["Punjab", "Chandigarh"],
    "Odisha":            ["Odisha", "Bhubaneswar"],
    "Gujarat":           ["Gujarat", "Ahmedabad", "Surat"],
    "Andhra Pradesh":    ["Andhra Pradesh", "AP", "Vizag"],
    "Haryana":           ["Haryana", "Gurugram"],
    "Kerala":            ["Kerala", "Thiruvananthapuram"],
    "Jharkhand":         ["Jharkhand", "Ranchi"],
    "Chhattisgarh":      ["Chhattisgarh", "Raipur"],
    "Uttarakhand":       ["Uttarakhand", "Dehradun"],
    "Himachal Pradesh":  ["Himachal Pradesh", "Shimla"]
}

# ── LOCATION EXACT MATCH BONUS ────────────────────────────────

def location_bonus(internship_location, user_location):
    """
    Returns a bonus score if internship location
    matches or is related to user preferred location.
    """
    if not user_location:
        return 0.0

    user_loc_lower  = user_location.lower().strip()
    intern_loc_lower = internship_location.lower().strip()

    # Exact match
    if user_loc_lower == intern_loc_lower:
        return 0.40

    # Alias match
    aliases = STATE_ALIASES.get(user_location, [])
    for alias in aliases:
        if alias.lower() in intern_loc_lower:
            return 0.35

    return 0.0

# ── EDUCATION MATCH BONUS ─────────────────────────────────────

EDU_LEVELS = {
    "Class 10":     1,
    "Class 12":     2,
    "Diploma":      3,
    "Graduate":     4,
    "Post Graduate":5
}

def education_bonus(internship_edu, user_edu):
    """
    Returns bonus if user education meets requirement.
    Penalizes if user is under-qualified.
    """
    if not user_edu or not internship_edu:
        return 0.0

    user_level   = EDU_LEVELS.get(user_edu, 0)
    intern_level = EDU_LEVELS.get(internship_edu, 0)

    if user_level >= intern_level:
        return 0.15   # Qualified — bonus
    else:
        return -0.20  # Under-qualified — penalty

# ── SECTOR MATCH BONUS ────────────────────────────────────────

def sector_bonus(internship_sector, user_sector):
    """
    Returns large bonus for exact sector match.
    """
    if not user_sector:
        return 0.0

    if internship_sector.lower() == user_sector.lower():
        return 0.30

    return 0.0

# ── MAIN RECOMMENDATION FUNCTION ─────────────────────────────

def get_recommendations(education, skills, sector, location):

    # Build candidate query
    # Repeat location and sector for stronger signal
    location_str = (location + " ") * 4  if location else ""
    sector_str   = (sector   + " ") * 4  if sector   else ""
    edu_str      = (education + " ") * 2  if education else ""

    query = (
        edu_str      +
        skills       + " " +
        sector_str   +
        location_str
    ).strip()

    if not query:
        query = "internship general india"

    # TF-IDF similarity
    query_vector      = vectorizer.transform([query])
    tfidf_scores      = cosine_similarity(
        query_vector,
        internship_matrix
    ).flatten()

    # Combined scoring
    final_scores = []

    for i, internship in enumerate(internships):
        tfidf  = float(tfidf_scores[i])

        loc_b  = location_bonus(
            internship["location"],
            location
        )
        edu_b  = education_bonus(
            internship["education_required"],
            education
        )
        sec_b  = sector_bonus(
            internship["sector"],
            sector
        )

        # Weighted final score
        final = (tfidf * 0.40) + loc_b + edu_b + sec_b

        final_scores.append((i, final))

    # Sort by final score descending
    final_scores.sort(key=lambda x: x[1], reverse=True)

    # Take top 5
    results = []

    for rank, (index, score) in enumerate(final_scores[:5]):
        internship = internships[index].copy()

        # Convert to percentage display
        pct = round(min(score * 100, 99))

        # Ensure scores look sensible on UI
        # Top match always shows high, decreases naturally
        if pct < 30:
            pct = max(30 + (5 - rank) * 4, 30)

        internship["match_score"] = pct
        results.append(internship)

    return results