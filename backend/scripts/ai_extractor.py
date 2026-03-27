from openai import OpenAI
import json

client = OpenAI()

def extract_with_ai(text):

    prompt = f"""
You are extracting structured curriculum data.

Return ONLY valid JSON.

STRICT RULES:
- Do NOT summarize
- Preserve exact wording
- Maintain hierarchy
- Capture ALL SLOs fully
- Separate activities correctly

JSON FORMAT:
{{
  "strand": "",
  "substrand": "",
  "slos": [
    {{
      "name": "",
      "description": ""
    }}
  ],
  "activities": {{
    "introduction": [],
    "development": [],
    "conclusion": [],
    "extended": []
  }},
  "competencies": [],
  "values": [],
  "pcis": []
}}

TEXT:
{text}
"""

    response = client.responses.create(
        model="GPT-5.4 nano",
        input=prompt
    )

    try:
        return json.loads(response.output[0].content[0].text)
    except Exception as e:
        print("AI parsing error:", e)
        return None
