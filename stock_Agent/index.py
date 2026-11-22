import os
import json  
from groq import Groq
from dotenv import load_dotenv
import yfinance as yf
from constant import FEW_SHOT_PROMT

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

def stock_price_checker(ticker_symbol: str) -> float:
    ticker = yf.Ticker(ticker_symbol.strip().upper())

    price = None

    try:
        price = ticker.fast_info["last_price"]
    except Exception as e:
        print(f"fast_info failed for {ticker_symbol}: {e!r}")

    if price is None or price != price: 
        try:
            hist = ticker.history(period="5d")
            if not hist.empty:
                price = hist["Close"].iloc[-1]
        except Exception as e:
            print(f"history failed for {ticker_symbol}: {e!r}")

    if price is None or price != price:
        raise ValueError(f"No price data found for ticker {ticker_symbol!r}.")
    return float(price)

tool_info={

    "type": "function",
    "function":{
        "name": "stock_price_checker",
        "description": "Get the current stock price for a given company by ticker symbol",  
        "parameters": {
            "type": "object",
            "properties": {
                "ticker_symbol": {
                    "type": "string",
                    "description": "Ticker symbol of the company, e.g. AAPL for Apple"
                }
            },
            "required": ["ticker_symbol"]
        }
    }

}

def askLLM(prompt: str) -> str:
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing.")

    client = Groq(api_key=api_key)
    messages = FEW_SHOT_PROMT + [{"role": "user", "content": prompt}]

    for _ in range(5):
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            temperature=0.5,
            tools=[tool_info]
        )

        msg = response.choices[0].message
        print("🚀 ~ askLLM ~ msg:", msg)

        if not msg.tool_calls:
            return msg.content

        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments
                        if isinstance(call.function.arguments, str)
                        else json.dumps(call.function.arguments),
                    },
                }
                for call in msg.tool_calls
            ],
        })

        for call in msg.tool_calls:
            if call.function.name == "stock_price_checker":
                args = call.function.arguments
                if isinstance(args, str):
                    args = json.loads(args)
                try:
                    result = stock_price_checker(args.get("ticker_symbol", ""))
                except Exception as e:
                    result = {"error": str(e)}
            else:
                result = {"error": f"Unknown tool {call.function.name}"}

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            })

    return "Sorry, I couldn't complete the request."

print(askLLM("what is current stock price of meta?"))