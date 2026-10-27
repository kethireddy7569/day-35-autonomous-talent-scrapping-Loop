import os
import json
from pathlib import Path

import requests
from dotenv import load_dotenv


# =========================================================
# 1. LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print("❌ OPENROUTER_API_KEY is missing in .env")
    exit()


# =========================================================
# 2. FIND DAY 34 JSON AUTOMATICALLY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
SEARCH_DIR = BASE_DIR.parent

print("\nSearching for Day 34 data...")

matches = list(
    SEARCH_DIR.rglob("day34_job_data.json")
)

if not matches:
    print("❌ day34_job_data.json not found.")
    print("Search location:", SEARCH_DIR)
    exit()

DAY34_FILE = matches[0]

print("✅ Day 34 file found:")
print(DAY34_FILE)


# =========================================================
# 3. READ DAY 34 DATA
# =========================================================

try:
    with open(
        DAY34_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        jobs = json.load(file)

except Exception as e:
    print("❌ Error reading Day 34 JSON:")
    print(e)
    exit()


if not isinstance(jobs, list):
    print("❌ Day 34 JSON must contain a list of jobs.")
    exit()

if not jobs:
    print("❌ No jobs found in Day 34.")
    exit()

print(f"✅ Loaded {len(jobs)} jobs from Day 34.")


# =========================================================
# 4. OPENROUTER CONFIGURATION
# =========================================================

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

MODEL = "openrouter/free"


# =========================================================
# 5. DAY 35 PROMPT
# =========================================================

prompt = f"""
You are an Autonomous Talent Sourcing Agent.

Analyze the job vacancies collected during Day 34.

Identify relevant technology and software talent opportunities.

Consider jobs related to:

- Python
- Artificial Intelligence
- Generative AI
- Machine Learning
- Data Science
- Data Engineering
- Backend Development
- Frontend Development
- Full Stack Development
- Software Engineering
- Automation
- Cloud
- DevOps
- Cybersecurity
- API Development

IMPORTANT RULES:

1. Use ONLY the jobs provided below.
2. Do NOT invent jobs.
3. Do NOT invent companies.
4. Do NOT invent job URLs.
5. Do NOT select only Python jobs.
6. Include different relevant technology roles.
7. Preserve the original job information.
8. Identify relevant technical skills.
9. Give a short reason why each selected job is relevant.
10. Return ONLY JSON.
11. No Markdown.
12. No ```json code fences.

Return this structure:

[
    {{
        "job_title": "string",
        "company": "string",
        "location": "string",
        "work_mode": "string",
        "employment_type": "string",
        "source": "string",
        "job_url": "string",
        "relevant_skills": [
            "skill1",
            "skill2"
        ],
        "relevance_reason": "string"
    }}
]

DAY 34 JOB DATA:

{json.dumps(jobs, indent=2, ensure_ascii=False)}
"""


# =========================================================
# 6. OPENROUTER REQUEST
# =========================================================

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": MODEL,
    "messages": [
        {
            "role": "system",
            "content": (
                "You are a professional autonomous "
                "talent sourcing and job classification agent."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    "temperature": 0.1
}


print("\nSending Day 34 jobs to OpenRouter...")


try:

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=120
    )

except requests.exceptions.RequestException as e:

    print("❌ OpenRouter connection error:")
    print(e)
    exit()

if response.status_code != 200:

    print("\n❌ OpenRouter API Error")
    print("Status Code:", response.status_code)
    print("Response:")
    print(response.text)
    exit()


try:

    response_data = response.json()

except json.JSONDecodeError:

    print("❌ OpenRouter returned invalid JSON.")
    print(response.text)
    exit()


try:

    ai_response = (
        response_data["choices"][0]
        ["message"]["content"]
    )

except (KeyError, IndexError, TypeError):

    print("❌ Unexpected OpenRouter response.")

    print(
        json.dumps(
            response_data,
            indent=2
        )
    )

    exit()


if not ai_response:
    print("❌ OpenRouter returned an empty response.")
    exit()


ai_response = ai_response.strip()

# Remove ```json if model returns it
if ai_response.startswith("```json"):
    ai_response = ai_response[7:]

# Remove ```
if ai_response.startswith("```"):
    ai_response = ai_response[3:]

if ai_response.endswith("```"):
    ai_response = ai_response[:-3]

ai_response = ai_response.strip()


try:

    relevant_jobs = json.loads(ai_response)

except json.JSONDecodeError:

    print("\n❌ AI returned invalid JSON.")

    print("\nAI Response:")
    print(ai_response)

    exit()


if isinstance(relevant_jobs, list):

    final_jobs = relevant_jobs

elif isinstance(relevant_jobs, dict):

    if "jobs" in relevant_jobs:

        final_jobs = relevant_jobs["jobs"]

    elif "relevant_jobs" in relevant_jobs:

        final_jobs = relevant_jobs["relevant_jobs"]

    else:

        print("❌ AI returned an unexpected JSON object.")

        print(
            json.dumps(
                relevant_jobs,
                indent=2
            )
        )

        exit()

else:

    print("❌ Unexpected AI response format.")
    print(relevant_jobs)
    exit()


if not isinstance(final_jobs, list):

    print("❌ Jobs data is not a list.")
    exit()


relevant_jobs = final_jobs

print(
    f"✅ AI identified {len(relevant_jobs)} relevant jobs."
)


OUTPUT_FILE = (
    BASE_DIR / "day35_relevant_jobs.json"
)

try:

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            relevant_jobs,
            file,
            indent=4,
            ensure_ascii=False
        )

except Exception as e:

    print("❌ Error saving output:")
    print(e)
    exit()


print("\n")
print("=" * 60)
print("DAY 35 COMPLETED SUCCESSFULLY")
print("=" * 60)

print(
    f"Day 34 jobs      : {len(jobs)}"
)

print(
    f"Relevant jobs    : {len(relevant_jobs)}"
)

print(
    f"Output file      : {OUTPUT_FILE}"
)

print("\nRelevant Jobs:")
print("=" * 60)


for index, job in enumerate(
    relevant_jobs,
    start=1
):

    print(
        f"\n{index}. "
        f"{job.get('job_title', 'N/A')}"
    )

    print(
        f"   Company      : "
        f"{job.get('company', 'N/A')}"
    )

    print(
        f"   Location     : "
        f"{job.get('location', 'N/A')}"
    )

    print(
        f"   Work Mode    : "
        f"{job.get('work_mode', 'N/A')}"
    )

    skills = job.get(
        "relevant_skills",
        []
    )

    if isinstance(skills, list):
        skills_text = ", ".join(skills)
    else:
        skills_text = str(skills)

    print(
        f"   Skills       : "
        f"{skills_text}"
    )

    print(
        f"   Reason       : "
        f"{job.get('relevance_reason', 'N/A')}"
    )

    print(
        f"   URL          : "
        f"{job.get('job_url', 'N/A')}"
    )

    print("-" * 60)


print("\n✅ Output saved successfully.")