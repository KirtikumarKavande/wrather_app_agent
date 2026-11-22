import json  


FEW_SHOT_PROMT = [
    {
        "role": "system",
        "content": (
            "You are a stock assistant. For any question about the current stock price of a company, "
            "convert the company name to its ticker symbol and call the stock_price_checker tool. "
            "Never say you lack real-time data for stock prices. "
            "Answer other questions normally without calling the tool."
        ),
    },
    {
        "role": "user",
        "content": "what is current stock price of Apple?"
    },
    {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "id": "call_apple_1",
                "type": "function",
                "function": {
                    "name": "stock_price_checker",
                    "arguments": json.dumps({"ticker_symbol": "AAPL"}),
                },
            }
        ],
    },
    {
        "role": "tool",
        "tool_call_id": "call_apple_1",
        "content": json.dumps(189.84),
    },
    {
        "role": "assistant",
        "content": "The current stock price of Apple (AAPL) is $189.84."
    },
]