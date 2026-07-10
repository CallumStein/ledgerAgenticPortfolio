import json
import os
from typing import List, Dict, Any
from tools.hledger_tools import run_hledger_command, get_balance, get_transactions, get_summary, add_transaction, add_income, add_expense
from core.config import API_KEY, MODEL_NAME, BASE_URL
from openai import OpenAI

class PortfolioAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL
        )
        self.model_name = MODEL_NAME
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_balance",
                    "description": "Get the current balance of all accounts in the hledger portfolio.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_transactions",
                    "description": "Get transactions for a specific account.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "account": {
                                "type": "string",
                                "description": "The name of the account to get transactions for.",
                            },
                        },
                        "required": ["account"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_summary",
                    "description": "Get a summary of the portfolio.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "add_income",
                    "description": "Add an income payment to your Commbank account. You just need to provide the amount, currency, and description.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {
                                "type": "number",
                                "description": "The amount of income.",
                            },
                            "currency": {
                                "type": "string",
                                "description": "The currency (e.g., AUD). Defaults to AUD.",
                            },
                            "description": {
                                "type": "string",
                                "description": "A description of the income (e.g., 'Salary').",
                            },
                        },
                        "required": ["amount", "description"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "add_transaction",
                    "description": "Add a transaction to the hledger portfolio. Provide the full hledger transaction string.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "transaction_string": {
                                "type": "string",
                                "description": "The full hledger transaction string, e.g., '2023-10-27 * Grocery Store\n    Expenses:Groceries    50.00 USD\n    Assets:Bank:CommBank Every Day  -50.00 USD'",
                            },
                        },
                        "required": ["transaction_string"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "add_expense",
                    "description": "Add an expense payment to your Commbank account. You just need to provide the amount, currency, and description.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {
                                "type": "number",
                                "description": "The amount of the expense.",
                            },
                            "currency": {
                                "type": "string",
                                "description": "The currency (e.g., AUD). Defaults to AUD.",
                            },
                            "description": {
                                "type": "string",
                                "description": "A description of the expense (e.g., 'Groceries').",
                            },
                        },
                        "required": ["amount", "description"],
                    },
                },
            },
        ]

    def run(self, user_query: str) -> str:
        """
        Main entry point for the agent to process user queries using an agentic loop.
        """
        messages = [
            {"role": "system", "content": f"You are a helpful financial assistant that can query a hledger portfolio. Use tools to answer user questions accurately. Available tools: {json.dumps(self.tools)}"},
            {"role": "user", "content": user_query},
        ]

        # Simple ReAct loop (limit to 5 iterations to avoid infinite loops)
        for _ in range(5):
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=self.tools,
            )
            
            message = response.choices[0].message
            messages.append(message)

            if not message.tool_calls:
                return message.content

            # Process tool calls
            tool_outputs = []
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                if function_name == "get_balance":
                    output = get_balance()
                elif function_name == "get_transactions":
                    output = get_transactions(arguments.get("account"))
                elif function_name == "get_summary":
                    output = get_summary()
                elif function_name == "add_transaction":
                    output = add_transaction(arguments.get("transaction_string"))
                elif function_name == "add_expense":
                    output = add_expense(
                        amount=arguments.get("amount"),
                        currency=arguments.get("currency", "AUD"),
                        description=arguments.get("description"),
                    )
                elif function_name == "add_income":
                    output = add_income(
                        amount=arguments.get("amount"),
                        currency=arguments.get("currency", "AUD"),
                        description=arguments.get("description"),
                    )
                else:
                    output = f"Error: Tool {function_name} not found."
                
                tool_outputs.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": str(output),
                })
            
            messages.extend(tool_outputs)

        return "I'm sorry, I reached the maximum number of iterations."
