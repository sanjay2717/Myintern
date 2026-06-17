/* ============================================
   Myintern — MAIN JAVASCRIPT
   ============================================ */

// ── SKILL TAGS SETUP ──────────────────────────

const SKILL_TAGS = [
  "Developer", "Java", "C++", "Python",
  "UI UX", "Frontend", "Android",
  "Digital Marketing", "SEO", "Social Media",
  "Video Editing", "After Effects",
  "Data Science", "Cybersecurity",
  "Teaching", "Farming", "Accounting"
];

function buildSkillTags() {
  const container = document.getElementById("skillTags");
  if (!container) return;

  SKILL_TAGS.forEach(function (skill) {
    const tag = document.createElement("span");
    tag.className = "skill-tag";
    tag.textContent = skill;

    tag.addEventListener("click", function () {
      tag.classList.toggle("active");
      updateSkillInput();
    });

    container.appendChild(tag);
  });
}

function updateSkillInput() {
  const activeTags = document.querySelectorAll(".skill-tag.active");
  const values = Array.from(activeTags).map(t => t.textContent);
  const input = document.getElementById("skills");

  // Merge typed input with tag selections
  const typed = input.dataset.typed || "";
  const tagString = values.join(", ");

  if (typed && tagString) {
    input.value = typed + ", " + tagString;
  } else {
    input.value = tagString || typed;
  }
}

// Save manually typed value separately
function initSkillInput() {
  const input = document.getElementById("skills");
  if (!input) return;

  input.addEventListener("input", function () {
    input.dataset.typed = input.value;
  });
}

// ── SECTOR COLOR MAP ─────────────────────────

const SECTOR_CLASSES = {
  "IT":             "sector-IT",
  "Agriculture":    "sector-Agriculture",
  "Health":         "sector-Health",
  "Education":      "sector-Education",
  "Finance":        "sector-Finance",
  "Manufacturing":  "sector-Manufacturing",
  "Retail":         "sector-Retail",
  "Infrastructure": "sector-Infrastructure"
};

const SECTOR_ICONS = {
  "IT":             "💻",
  "Agriculture":    "🌾",
  "Health":         "🏥",
  "Education":      "📚",
  "Finance":        "💰",
  "Manufacturing":  "🏭",
  "Retail":         "🛍️",
  "Infrastructure": "🏗️"
};

// ── MATCH CIRCLE CLASS ────────────────────────

function getMatchClass(score) {
  if (score >= 75) return "high";
  if (score >= 45) return "medium";
  return "low";
}

// ── BUILD CARD HTML ───────────────────────────

function buildCard(item, index) {
  const matchClass   = getMatchClass(item.match_score);
  const sectorClass  = SECTOR_CLASSES[item.sector] || "sector-IT";
  const sectorIcon   = SECTOR_ICONS[item.sector] || "🏢";
  const rankLabel    = index === 0 ? "⭐ TOP MATCH" : `#${index + 1} MATCH`;
  const isTopMatch   = index === 0 ? "top-match" : "";

  const noExpTag = item.description.toLowerCase().includes("no prior")
    ? `<span class="no-experience-tag">✅ No Experience Needed</span>`
    : "";

  // Animation delay per card
  const delay = index * 0.1;

  return `
    <div class="card ${isTopMatch}" style="animation-delay: ${delay}s">

      <div class="card-rank">${rankLabel}</div>

      <div class="card-top">
        <div class="card-title-block">
          <div class="card-title">${item.title}</div>
          <div class="card-company">
            🏢 ${item.company}
          </div>
        </div>
        <div class="match-circle ${matchClass}">
          <span class="match-percent">${item.match_score}%</span>
          <span class="match-label">Match</span>
        </div>
      </div>

      <div class="card-mid">
        <span class="sector-badge ${sectorClass}">
          ${sectorIcon} ${item.sector}
        </span>
        ${noExpTag}
      </div>

      <div class="card-details">
        <div class="detail-item">
          <div class="detail-icon-box">📍</div>
          <div class="detail-text">
            <strong>Location</strong>
            <span>${item.location}</span>
          </div>
        </div>
        <div class="detail-item">
          <div class="detail-icon-box">🎓</div>
          <div class="detail-text">
            <strong>Education</strong>
            <span>${item.education_required}</span>
          </div>
        </div>
        <div class="detail-item">
          <div class="detail-icon-box">💰</div>
          <div class="detail-text">
            <strong>Stipend</strong>
            <span>₹${parseInt(item.stipend).toLocaleString('en-IN')} / mo</span>
          </div>
        </div>
        <div class="detail-item">
          <div class="detail-icon-box">⏱️</div>
          <div class="detail-text">
            <strong>Duration</strong>
            <span>${item.duration} Month${item.duration > 1 ? 's' : ''}</span>
          </div>
        </div>
      </div>

      <button class="apply-btn" onclick="handleApply('${item.title}', '${item.company}')">
        Apply Now
        <span class="btn-arrow">→</span>
      </button>

    </div>
  `;
}

// ── APPLY HANDLER ─────────────────────────────

function handleApply(title, company) {
  alert(`Redirecting to PM Internship Portal for:\n\n"${title}"\n${company}\n\nIn production this will open the official application page.`);
}

// ── SHOW LOADER ───────────────────────────────

function showLoader() {
  document.getElementById("loader").style.display = "block";
  document.getElementById("resultsSection").style.display = "none";
}

function hideLoader() {
  document.getElementById("loader").style.display = "none";
}

// ── SHOW RESULTS ──────────────────────────────

function showResults(data) {
  const section    = document.getElementById("resultsSection");
  const countBadge = document.getElementById("resultsCount");
  const cardsList  = document.getElementById("cardsList");

  cardsList.innerHTML = "";
  section.style.display = "block";

  if (!data.success || data.recommendations.length === 0) {
    countBadge.textContent = "0";
    cardsList.innerHTML = `
      <div class="no-results">
        <div class="no-results-icon">🔍</div>
        <h3>No matches found</h3>
        <p>Try selecting a different sector or location to find relevant internships.</p>
      </div>
    `;
    return;
  }

  countBadge.textContent = data.count;

  data.recommendations.forEach(function (item, index) {
    cardsList.insertAdjacentHTML("beforeend", buildCard(item, index));
  });

  // Smooth scroll to results
  setTimeout(function () {
    section.scrollIntoView({ behavior: "smooth", block: "start" });
  }, 100);
}

// ── RESET FORM ────────────────────────────────

function resetForm() {
  document.getElementById("recommendForm").reset();
  document.getElementById("resultsSection").style.display = "none";

  // Clear active skill tags
  document.querySelectorAll(".skill-tag.active").forEach(function (tag) {
    tag.classList.remove("active");
  });

  const input = document.getElementById("skills");
  input.value = "";
  input.dataset.typed = "";

  // Scroll back to form
  document.getElementById("recommendForm")
    .scrollIntoView({ behavior: "smooth", block: "start" });
}

// ── FORM SUBMIT ───────────────────────────────

async function handleSubmit(e) {
  e.preventDefault();

  const education = document.getElementById("education").value;
  const skills    = document.getElementById("skills").value;
  const sector    = document.getElementById("sector").value;
  const location  = document.getElementById("location").value;

  showLoader();

  try {
    const response = await fetch("/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ education, skills, sector, location })
    });

    if (!response.ok) {
      throw new Error("Server error: " + response.status);
    }

    const data = await response.json();
    hideLoader();
    showResults(data);

  } catch (error) {
    hideLoader();
    document.getElementById("resultsSection").style.display = "block";
    document.getElementById("cardsList").innerHTML = `
      <div class="no-results">
        <div class="no-results-icon">⚠️</div>
        <h3>Something went wrong</h3>
        <p>Please check your connection and try again.</p>
      </div>
    `;
  }
}

// ── INIT ──────────────────────────────────────

document.addEventListener("DOMContentLoaded", function () {
  buildSkillTags();
  initSkillInput();

  const form = document.getElementById("recommendForm");
  if (form) {
    form.addEventListener("submit", handleSubmit);
  }

  const resetBtn = document.getElementById("resetBtn");
  if (resetBtn) {
    resetBtn.addEventListener("click", resetForm);
  }
});