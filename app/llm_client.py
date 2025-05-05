import os, openai
openai.api_key = os.getenv("OPENAI_API_KEY")

PROMPT = """
You are a healthcare scheduler.
Patient profile:
{patient}

Available slots:
{slots}

Suggest up to 3 optimal appointment times as JSON:
[{{"start":"…","end":"…","reason":"…"}}, …]
"""

async def recommend_slots(patient: dict, slots: list[dict]) -> str:
  # formatting the prompt with patient and slot data
  content = PROMPT.format(patient=patient, slots=slots)
  # calling OpenAI asynchronously
  resp = await openai.ChatCompletion.acreate(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": content}],
    max_tokens=300,
  )
  # returning the raw assistant message
  return resp.choices[0].message.content
