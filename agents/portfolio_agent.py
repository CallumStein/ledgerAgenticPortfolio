import json
from typing import Any

from openai import OpenAI

from tools.hledger_tools import (
    run_hledger_command,
    get_balance,
    get_transactions,
    get_summary,
    add_bank_transaction,
    add_income,
    add_expense,
)
from core.config import API_KEY, MODEL_NAME, BASE_URL


class PortfolioAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL,
        )
        self.model_name = MODEL_NAME

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_balance",
                    "description": (
                        "Get the current balance of all accounts in the "
                        "hledger portfolio."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
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
                                "description": (
                                    "The full hledger account name to retrieve "
                                    "transactions for."
                                ),
                            },
                        },
                        "required": ["account"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_summary",
                    "description": "Get a summary of the hledger portfolio.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "add_income",
                    "description": (
                        "Record income received into the default CommBank "
                        "account. Provide the positive amount, currency, and "
                        "description."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {
                                "type": "number",
                                "exclusiveMinimum": 0,
                                "description": (
                                    "The positive amount of income received."
                                ),
                            },
                            "currency": {
                                "type": "string",
                                "description": (
                                    "The currency code, such as AUD. "
                                    "Defaults to AUD."
                                ),
                            },
                            "description": {
                                "type": "string",
                                "description": (
                                    "A description of the income, such as Salary."
                                ),
                            },
                            "transaction_date": {
                                "type": "string",
                                "description": (
                                    "Optional transaction date in YYYY-MM-DD format. "
                                    "Convert dates from the user's request into this format. "
                                    "For example, 06/06/2026 becomes 2026-06-06. "
                                    "If no date is supplied, omit this property."
                                ),
                            },
                        },
                        "required": ["amount", "description"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "add_expense",
                    "description": (
                        "Record an expense paid from the default CommBank "
                        "account. Provide the positive amount, currency, and "
                        "description."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {
                                "type": "number",
                                "exclusiveMinimum": 0,
                                "description": (
                                    "The positive amount of the expense."
                                ),
                            },
                            "currency": {
                                "type": "string",
                                "description": (
                                    "The currency code, such as AUD. "
                                    "Defaults to AUD."
                                ),
                            },
                            "description": {
                                "type": "string",
                                "description": (
                                    "A description of the expense, "
                                    "such as Groceries."
                                ),
                            },
                            "transaction_date": {
                                "type": "string",
                                "description": (
                                    "Optional transaction date in YYYY-MM-DD format. "
                                    "Convert dates from the user's request into this format. "
                                    "For example, 06/06/2026 becomes 2026-06-06. "
                                    "If no date is supplied, omit this property."
                                ),
                            },
                        },
                        "required": ["amount", "description"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "add_bank_transaction",
                    "description": (
                        "Add a transfer between two bank accounts. "
                        "Use the supplied transaction date when provided; "
                        "otherwise the tool will use today's date."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {
                                "type": "number",
                                "description": "The positive amount to transfer.",
                            },
                            "currency": {
                                "type": "string",
                                "description": "The currency, such as AUD.",
                            },
                            "description": {
                                "type": "string",
                                "description": "A description of the transfer.",
                            },
                            "source_account": {
                                "type": "string",
                                "description": "The bank account the money leaves.",
                            },
                            "destination_account": {
                                "type": "string",
                                "description": "The bank account the money enters.",
                            },
                            "transaction_date": {
                                "type": "string",
                                "description": (
                                    "Optional transaction date in YYYY-MM-DD format. "
                                    "Convert dates from the user's request into this format. "
                                    "For example, 06/06/2026 becomes 2026-06-06. "
                                    "If no date is supplied, omit this property."
                                ),
                            },
                        },
                        "required": [
                            "amount",
                            "currency",
                            "description",
                            "source_account",
                            "destination_account",
                        ],
                        "additionalProperties": False,
                    },
                },
            },
        ]

    def run(self, user_query: str) -> str:
        """
        Process a user query using a tool-calling agent loop.
        """
        messages: list[Any] = [
            {
                "role": "system",
                "content": (
                    "You are a helpful financial assistant that manages an "
                    "hledger portfolio.\n\n"
                    "Use the available tools whenever the user asks to read or "
                    "modify financial data.\n\n"
                    "Important rules:\n"
                    "- Use add_bank_transaction only for transfers between two "
                    "bank accounts.\n"
                    "- Use add_income for money received from an income account.\n"
                    "- Use add_expense for purchases or expenses.\n"
                    "- Bank transfer amounts must always be positive.\n"
                    "- The source_account is the account money leaves.\n"
                    "- The destination_account is the account money enters.\n"
                    "- When the user supplies a transaction date, convert it "
                    "to YYYY-MM-DD before calling a write tool. For example, "
                    "06/06/2026 becomes 2026-06-06. If no date is supplied, "
                    "omit transaction_date so the tool uses today's date.\n"
                    "- Do not invent an account name when the user has not "
                    "provided enough information.\n"
                    "- Confirm the result after a write tool completes."
                ),
            },
            {
                "role": "user",
                "content": user_query,
            },
        ]

        # Limit the agent loop to avoid infinite tool-call cycles.
        for _ in range(5):
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=self.tools,
            )

            message = response.choices[0].message
            messages.append(message)

            if not message.tool_calls:
                return message.content or "No response was generated."

            tool_outputs = []

            for tool_call in message.tool_calls:
                function_name = tool_call.function.name

                try:
                    arguments = json.loads(
                        tool_call.function.arguments or "{}"
                    )
                    output = self._execute_tool(
                        function_name=function_name,
                        arguments=arguments,
                    )
                except json.JSONDecodeError as error:
                    output = (
                        "Error: The tool arguments were not valid JSON. "
                        f"{error}"
                    )
                except Exception as error:
                    output = f"Error while executing {function_name}: {error}"

                tool_outputs.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": str(output),
                    }
                )

            messages.extend(tool_outputs)

        return "I'm sorry, I reached the maximum number of iterations."

    def _execute_tool(
        self,
        function_name: str,
        arguments: dict[str, Any],
    ) -> str:
        """
        Execute a tool requested by the model.
        """
        if function_name == "get_balance":
            return get_balance()

        if function_name == "get_transactions":
            account = arguments.get("account")

            if not account:
                return "Error: An account name is required."

            return get_transactions(account)

        if function_name == "get_summary":
            return get_summary()

        if function_name == "add_expense":
            return add_expense(
                amount=arguments.get("amount"),
                currency=arguments.get("currency", "AUD"),
                description=arguments.get("description"),
                transaction_date=arguments.get("transaction_date"),
            )

        if function_name == "add_income":
            return add_income(
                amount=arguments.get("amount"),
                currency=arguments.get("currency", "AUD"),
                description=arguments.get("description"),
                transaction_date=arguments.get("transaction_date"),
            )

        if function_name == "add_bank_transaction":
            return add_bank_transaction(
                amount=arguments.get("amount"),
                currency=arguments.get("currency", "AUD"),
                description=arguments.get("description"),
                source_account=arguments.get("source_account"),
                destination_account=arguments.get("destination_account"),
                transaction_date=arguments.get("transaction_date"),
            )

        return f"Error: Tool {function_name} not found."