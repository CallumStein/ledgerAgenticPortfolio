from core.config import HLEDGER_FILE, INCOME_FILE, EXPENSES_FILE, BANK_FILE
import subprocess
import json
from typing import List, Dict
from datetime import datetime

def run_hledger_command(command: str) -> str:

    """Executes a hledger command and returns the output."""
    try:
        # We'll assume the hledger file is in the current directory or specified
        # For now, let's just run it. We might need to adjust this to use -f
        result = subprocess.run(
            ["hledger", "-f", HLEDGER_FILE] + command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        return "Error: hledger command not found."

def get_balance() -> str:
    """Gets the current balance of all accounts."""
    return run_hledger_command("balance")

def get_summary() -> str:
    """Gets a summary of the portfolio."""
    return run_hledger_command("balance")

def get_transactions(account: str) -> str:
    """Gets transactions for a specific account."""
    return run_hledger_command(f"register {account}")

def add_transaction(transaction_string: str) -> str:
    """Adds a transaction to the hledger portfolio."""
    try:
        # We use hledger to check if the transaction is valid before adding it.
        # This is a bit tricky because hledger doesn't have a "check only one transaction" command easily
        # but we can append it to a temporary file and run hledger on that.
        
        temp_file = "temp_transaction.hledger"
        with open(HLEDGER_FILE, "r") as f:
            content = f.read()
        
        with open(temp_file, "w") as f:
            f.write(content + "\n" + transaction_string)
        
        # Check if the temporary file is valid
        result = subprocess.run(
            ["hledger", "-f", temp_file, "balance"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # If valid, append to the real file
        with open(HLEDGER_FILE, "a") as f:
            f.write("\n" + transaction_string)
        
        import os
        os.remove(temp_file)
        return "Transaction added successfully."
    except subprocess.CalledProcessError as e:
        return f"Error: The transaction is invalid. {e.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

def add_income(amount: float, currency: str, description: str) -> str:
    """Adds an income transaction to the Assets:Bank:CommBank Every Day account."""
    try:
        date = datetime.now().strftime("%Y-%m-%d")
        # Constructing a simple income transaction.
        # We assume the source is 'Income' and the destination is 'Assets:Bank:CommBank Every Day'.
        transaction_string = f"{date} * {description}\n    Income:Source    {amount:.2f} {currency}\n    Assets:Bank:CommBank Every Day  -{amount:.2f} {currency}"
        
        temp_file = "temp_transaction.hledger"
        with open(INCOME_FILE, "r") as f:
            content = f.read()
        
        with open(temp_file, "w") as f:
            f.write(content + "\n" + transaction_string)
        
        # Check if the temporary file is valid
        result = subprocess.run(
            ["hledger", "-f", temp_file, "balance"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # If valid, append to the real file
        with open(INCOME_FILE, "a") as f:
            f.write("\n" + transaction_string)
        
        import os
        os.remove(temp_file)
        return f"Successfully added income: {description} ({amount:.2f} {currency})"
    except subprocess.CalledProcessError as e:
        return f"Error: The transaction is invalid. {e.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

def add_expense(amount: float, currency: str, description: str) -> str:
    """Adds an expense transaction to the Assets:Bank:CommBank Every Day account."""
    try:
        date = datetime.now().strftime("%Y-%m-%d")
        # Constructing a simple expense transaction.
        # We assume the source is 'Expenses' and the destination is 'Assets:Bank:CommBank Every Day'.
        transaction_string = f"{date} * {description}\n    Expenses:Source    {amount:.2f} {currency}\n    Assets:Bank:CommBank Every Day  -{amount:.2f} {currency}"
        
        temp_file = "temp_transaction.hledger"
        with open(EXPENSES_FILE, "r") as f:
            content = f.read()
        
        with open(temp_file, "w") as f:
            f.write(content + "\n" + transaction_string)
        
        # Check if the temporary file is valid
        result = subprocess.run(
            ["hledger", "-f", temp_file, "balance"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # If valid, append to the real file
        with open(EXPENSES_FILE, "a") as f:
            f.write("\n" + transaction_string)
        
        import os
        os.remove(temp_file)
        return f"Successfully added expense: {description} ({amount:.2f} {currency})"
    except subprocess.CalledProcessError as e:
        return f"Error: The transaction is invalid. {e.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"
