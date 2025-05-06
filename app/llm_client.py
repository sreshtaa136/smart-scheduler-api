import os, re, json
from openai import OpenAI
from fastapi.concurrency import run_in_threadpool

# instantiate the new client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT = """
You are a healthcare scheduler.
Patient profile:
{patient}

Available slots:
{slots}

Suggest up to 3 optimal appointment times as JSON. Respond with ONLY a JSON array (no prose, no code fences):
[{{"start":"…","end":"…","reason":"…"}}, …]
"""

async def recommend_slots(patient: dict, slots: list[dict]) -> str:
  # formatting the prompt with patient and slot data
  content = PROMPT.format(patient=patient, slots=slots)
  # calling OpenAI asynchronously
  resp = await run_in_threadpool(
    client.chat.completions.create,
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": content}],
    max_tokens=300,
  )
  raw = resp.choices[0].message.content

  # extract JSON array
  # look for a standalone array; if fences exist, strip them
  m = re.search(r"(\[\s*(?:.|\s)*\])", raw)
  json_text = m.group(1) if m else raw.strip()

  # 4) Parse and return
  try:
    return json.loads(json_text)
  except json.JSONDecodeError:
    # in case the model still hallucinates extra text, try a looser strip
    return json.loads(raw.strip())
