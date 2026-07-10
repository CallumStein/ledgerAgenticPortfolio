from core.config import HLEDGER_FILE, INCOME_FILE, EXPENSES_FILE, BANK_FILE
import os
import subprocess
import json
from typing import List, Dict
from datetime import datetime

def run_hledger_command(
        command: str
    ) -> str:
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

def get_transactions(
        account: str
    ) -> str:
    """Gets transactions for a specific account."""
    return run_hledger_command(f"register {account}")

def add_transaction(
        transaction_string: str
    ) -> str:
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

def add_income(
    amount: float,
    currency: str,
    description: str,
    transaction_date: str = None,
) -> str:
    """Adds an income transaction to the CommBank Every Day account."""
    temp_file = "temp_income_transaction.hledger"

    try:
        if transaction_date:
            date = datetime.strptime(
                transaction_date,
                "%Y-%m-%d",
            ).strftime("%Y-%m-%d")
        else:
            date = datetime.now().strftime("%Y-%m-%d")

        transaction_string = (
            f"{date} * {description}\n"
            f"    Income:Source    {amount:.2f} {currency}\n"
            f"    Assets:Bank:CommBank Every Day    -{amount:.2f} {currency}"
        )

        with open(INCOME_FILE, "r") as f:
            content = f.read()

        with open(temp_file, "w") as f:
            f.write(content + "\n" + transaction_string)

        subprocess.run(
            ["hledger", "-f", temp_file, "balance"],
            capture_output=True,
            text=True,
            check=True,
        )

        with open(INCOME_FILE, "a") as f:
            f.write("\n" + transaction_string)

        return (
            f"Successfully added income on {date}: "
            f"{description} ({amount:.2f} {currency})"
        )

    except ValueError:
        return "Error: The date must use the YYYY-MM-DD format."

    except subprocess.CalledProcessError as e:
        return f"Error: The transaction is invalid. {e.stderr}"

    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def add_expense(
    amount: float,
    currency: str,
    description: str,
    transaction_date: str = None,
) -> str:
    """Adds an expense transaction to the CommBank Every Day account."""
    temp_file = "temp_expense_transaction.hledger"

    try:
        if transaction_date:
            date = datetime.strptime(
                transaction_date,
                "%Y-%m-%d",
            ).strftime("%Y-%m-%d")
        else:
            date = datetime.now().strftime("%Y-%m-%d")

        transaction_string = (
            f"{date} * {description}\n"
            f"    Expenses:Source    {amount:.2f} {currency}\n"
            f"    Assets:Bank:CommBank Every Day    -{amount:.2f} {currency}"
        )

        with open(EXPENSES_FILE, "r") as f:
            content = f.read()

        with open(temp_file, "w") as f:
            f.write(content + "\n" + transaction_string)

        subprocess.run(
            ["hledger", "-f", temp_file, "balance"],
            capture_output=True,
            text=True,
            check=True,
        )

        with open(EXPENSES_FILE, "a") as f:
            f.write("\n" + transaction_string)

        return (
            f"Successfully added expense on {date}: "
            f"{description} ({amount:.2f} {currency})"
        )

    except ValueError:
        return "Error: The date must use the YYYY-MM-DD format."

    except subprocess.CalledProcessError as e:
        return f"Error: The transaction is invalid. {e.stderr}"

    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
def add_bank_transaction(
    amount: float,
    currency: str,
    description: str,
    source_account: str,
    destination_account: str,
    transaction_date: str = None,
) -> str:
    """Adds a transfer between two bank accounts."""
    temp_file = "temp_bank_transaction.hledger"

    try:
        if transaction_date:
            date = datetime.strptime(
                transaction_date,
                "%Y-%m-%d",
            ).strftime("%Y-%m-%d")
        else:
            date = datetime.now().strftime("%Y-%m-%d")

        transaction_string = (
            f"{date} * {description}\n"
            f"    {destination_account}    {amount:.2f} {currency}\n"
            f"    {source_account}    -{amount:.2f} {currency}"
        )

        with open(BANK_FILE, "r") as f:
            content = f.read()

        with open(temp_file, "w") as f:
            f.write(content + "\n" + transaction_string)

        subprocess.run(
            ["hledger", "-f", temp_file, "balance"],
            capture_output=True,
            text=True,
            check=True,
        )

        with open(BANK_FILE, "a") as f:
            f.write("\n" + transaction_string)

        return (
            f"Successfully transferred {amount:.2f} {currency} "
            f"from {source_account} to {destination_account} "
            f"on {date}"
        )

    except ValueError:
        return "Error: The date must use the YYYY-MM-DD format."

    except subprocess.CalledProcessError as e:
        return f"Error: The transaction is invalid. {e.stderr}"

    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)