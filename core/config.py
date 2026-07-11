import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Ledger folder
LEDGER_DIR = BASE_DIR / "ledgers"

HLEDGER_FILE = os.getenv(
    "HLEDGER_FILE",
    str(LEDGER_DIR / "portfolio.hledger"),
)

INCOME_FILE = os.getenv(
    "INCOME_FILE",
    str(LEDGER_DIR / "income.hledger"),
)

EXPENSES_FILE = os.getenv(
    "EXPENSES_FILE",
    str(LEDGER_DIR / "expenses.hledger"),
)

BANK_FILE = os.getenv(
    "BANK_FILE",
    str(LEDGER_DIR / "bank.hledger"),
)

# Statements folder (useful for your CSV importer)
STATEMENTS_DIR = BASE_DIR / "statements"

CURRENCY = os.getenv("CURRENCY", "AUD")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
API_KEY = os.getenv("API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "https://api.openai.com/v1")



# import os
# from dotenv import load_dotenv

# load_dotenv()

# HLEDGER_FILE = os.getenv("HLEDGER_FILE", "portfolio.hledger")
# INCOME_FILE = os.getenv("INCOME_FILE", "income.hledger")
# EXPENSES_FILE = os.getenv("EXPENSES_FILE", "expenses.hledger")
# BANK_FILE = os.getenv("BANK_FILE", "bank.hledger")
# CURRENCY = os.getenv("CURRENCY", "AUD")
# MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
# API_KEY = os.getenv("API_KEY", "")
# BASE_URL = os.getenv("BASE_URL", "https://api.openai.com/v1")
