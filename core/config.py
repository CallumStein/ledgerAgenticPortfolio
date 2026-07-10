import os
from dotenv import load_dotenv

load_dotenv()

HLEDGER_FILE = os.getenv("HLEDGER_FILE", "portfolio.hledger")
INCOME_FILE = os.getenv("INCOME_FILE", "income.hledger")
EXPENSES_FILE = os.getenv("EXPENSES_FILE", "expenses.hledger")
BANK_FILE = os.getenv("BANK_FILE", "bank.hledger")
CURRENCY = os.getenv("CURRENCY", "AUD")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
API_KEY = os.getenv("API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "https://api.openai.com/v1")
