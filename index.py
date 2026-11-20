import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

weatherDB = {
    "london": {"temperature": 15, "humidity": 80, "condition": "Cloudy"},
    "newyork": {"temperature": 20, "humidity": 70, "condition": "Sunny"},
    "delhi": {"temperature": 30, "humidity": 60, "condition": "Hot"},
    "sydney": {"temperature": 25, "humidity": 50, "condition": "Rainy"},
    "mumbai": {"temperature": 28, "humidity": 75, "condition": "Humid"},
    "bangalore": {"temperature": 22, "humidity": 65, "condition": "Pleasant"},
    "bali": {"temperature": 27, "humidity": 85, "condition": "Tropical"},
}

def get_weather(location: str) -> dict:
    # "London, UK" -> "london" ; "New York" -> "newyork"
    key = location.split(",")[0].strip().lower().replace(" ", "")
    data = weatherDB.get(key)
    if not data:
        return {"error": f"No data for location: {location}"}
    return {"location": key, **data}

weather_schema = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a given city",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name only, e.g. London"
                }
            },
            "required": ["location"]
        }
    }
}

def askLLM(prompt: str) -> str:
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing.")

    client = Groq(api_key=api_key)
    messages = [{"role": "user", "content": prompt}]

    while True:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            temperature=0.5,
            max_tokens=1000,
            tools=[weather_schema],      # tools must be sent on EVERY call
        )

        msg = response.choices[0].message
        print("🚀 ~ askLLM ~ msg:", msg)

        # No tool calls -> this is the final answer, exit the loop
        if not msg.tool_calls:
            return msg.content

        # Keep the assistant's tool-call message in history
        messages.append(msg)

        # Run every tool call the model asked for
        for call in msg.tool_calls:
            if call.function.name == "get_weather":
                args = call.function.arguments
                if isinstance(args, str):
                    args = json.loads(args)
                result = get_weather(args.get("location", ""))

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result),
                })

print(askLLM("What is the weather in london compared to newyork?"))