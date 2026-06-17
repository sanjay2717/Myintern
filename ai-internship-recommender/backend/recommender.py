import json
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --------------------------------------------------
# STEP 1 - Load internships from JSON file
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "internships.json")

with open(JSON_PATH, "r") as f:
    internships = json.load(f)

# --------------------------------------------------
# STEP 2 - Combine all fields into one text per internship
# --------------------------------------------------

def build_internship_text(internship):
    return (
        internship["title"] + " " +
        internship["sector"] + " " +
        internship["location"] + " " +
        internship["education_required"] + " " +
        internship["skills_required"] + " " +
        internship["description"]
    )

internship_texts = [build_internship_text(i) for i in internships]

# --------------------------------------------------
# STEP 3 - Build TF-IDF vectorizer at startup
# --------------------------------------------------

vectorizer = TfidfVectorizer(stop_words="english")
internship_matrix = vectorizer.fit_transform(internship_texts)

# --------------------------------------------------
# STEP 4 - Recommendation function
# --------------------------------------------------

def get_recommendations(education, skills, sector, location):

    # Build candidate query string from inputs
    query = (
        education + " " +
        skills + " " +
        sector + " " +
        location
    )

    # Transform query using the same vectorizer
    query_vector = vectorizer.transform([query])

    # Calculate cosine similarity scores
    similarity_scores = cosine_similarity(
        query_vector,
        internship_matrix
    ).flatten()

    # Get top 5 indices sorted by score descending
    top_indices = similarity_scores.argsort()[::-1][:5]

    # Build result list
    results = []

    for index in top_indices:
        internship = internships[index].copy()

        # Convert score to percentage
        score = round(float(similarity_scores[index]) * 100)

        # Minimum score floor so results always show
        if score < 10:
            score = 10 + int(index)

        internship["match_score"] = score
        results.append(internship)

    return results