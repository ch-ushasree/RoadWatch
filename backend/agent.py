import os
import json
from groq import Groq
from backend.tools import (
    lookup_road, get_budget, get_officer,
    get_accountability_score, draft_complaint
)

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "tool_lookup_road",
            "description": "Look up road details by location name or area.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_budget",
            "description": "Get budget and spending for a road using its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "road_id": {"type": "integer"}
                },
                "required": ["road_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_officer",
            "description": "Get responsible officer contact details for a road using its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "road_id": {"type": "integer"}
                },
                "required": ["road_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_accountability_score",
            "description": "Calculate accountability score for a road.",
            "parameters": {
                "type": "object",
                "properties": {
                    "road_id": {"type": "integer"}
                },
                "required": ["road_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_draft_complaint",
            "description": "Draft a formal complaint email to the responsible officer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "road_name": {"type": "string"},
                    "issue": {"type": "string"},
                    "officer_name": {"type": "string"},
                    "officer_email": {"type": "string"},
                    "officer_designation": {"type": "string"},
                    "department": {"type": "string"}
                },
                "required": ["road_name", "issue", "officer_name", "officer_email", "officer_designation", "department"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are RoadWatch AI - a helpful assistant that helps Indian citizens monitor road quality, track public spending, and report issues to authorities.

You have access to a database of roads, budgets, contractors, and responsible officers in Hyderabad, India.

When a user asks about a road or area:
1. First call tool_lookup_road to find matching roads
2. If they want budget info, call tool_get_budget with the road_id
3. If they want to know who is responsible, call tool_get_officer with the road_id
4. If they want accountability info, call tool_accountability_score
5. If they want to file a complaint, first lookup the road, get the officer, then call tool_draft_complaint

Always be helpful, factual, and cite data sources. Format currency with Cr/Lakh notation.
If a road is not found, say so honestly and suggest nearby areas."""


def execute_tool(name: str, args: dict) -> str:
    if name == "tool_lookup_road":
        return json.dumps(lookup_road(args["location"]))
    elif name == "tool_get_budget":
        return json.dumps(get_budget(args["road_id"]))
    elif name == "tool_get_officer":
        return json.dumps(get_officer(args["road_id"]))
    elif name == "tool_accountability_score":
        return json.dumps(get_accountability_score(args["road_id"]))
    elif name == "tool_draft_complaint":
        return json.dumps(draft_complaint(
            args["road_name"], args["issue"], args["officer_name"],
            args["officer_email"], args["officer_designation"], args["department"]
        ))
    return json.dumps({"error": "Unknown tool"})


def build_agent():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Please add it to your .env file.")
    return Groq(api_key=api_key)


def chat(client, user_message: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    for _ in range(5):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
            max_tokens=1000
        )

        msg = response.choices[0].message

        if not msg.tool_calls:
            return msg.content or "I could not find information for that query."

        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in msg.tool_calls
            ]
        })

        for tc in msg.tool_calls:
            result = execute_tool(tc.function.name, json.loads(tc.function.arguments))
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result
            })

    return msg.content or "I could not complete the request."


def analyze_photo(image_bytes: bytes) -> str:
    import base64
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
                    },
                    {
                        "type": "text",
                        "text": """You are a road damage assessment AI. Analyze this image and provide:
1. Type of damage (pothole, crack, waterlogging, broken divider, etc.)
2. Severity (Minor / Moderate / Severe)
3. Estimated size if visible
4. Safety risk to road users
5. Recommended action

Be specific and factual. Format as a short paragraph suitable for an official complaint."""
                    }
                ]
            }
        ],
        max_tokens=300
    )
    return response.choices[0].message.content