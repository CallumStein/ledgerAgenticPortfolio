from core.config import HLEDGER_FILE, INCOME_FILE, EXPENSES_FILE, BANK_FILE
import os
import csv
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


def _normalise_bank_account(bank_account: str) -> str:
    account_aliases = {
        "commbank every day": "Assets:Bank:CommBank Every Day",
        "commbank everyday": "Assets:Bank:CommBank Every Day",
        "commbank": "Assets:Bank:CommBank Every Day",
        "st george": "Assets:Bank:StGeorge Incentive Saver",
        "st george incentive saver": "Assets:Bank:StGeorge Incentive Saver",
    }

    cleaned_account = bank_account.strip()

    if cleaned_account.lower().startswith("assets:bank:"):
        return cleaned_account

    resolved_account = account_aliases.get(cleaned_account.lower())

    if not resolved_account:
        raise ValueError(
            f"Unknown bank account: {bank_account}"
        )

    return resolved_account


def _validate_and_append_transactions(
    ledger_file: str,
    transactions: list[str],
    temp_file: str,
) -> None:
    """
    Validates transactions against an hledger file, then appends them.

    Nothing is written to the real ledger unless hledger validation succeeds.
    """
    if not transactions:
        return

    with open(ledger_file, "r", encoding="utf-8") as file:
        existing_content = file.read()

    transaction_content = "\n\n".join(transactions)

    with open(temp_file, "w", encoding="utf-8") as file:
        file.write(existing_content)

        if existing_content and not existing_content.endswith("\n"):
            file.write("\n")

        file.write("\n")
        file.write(transaction_content)
        file.write("\n")

    subprocess.run(
        ["hledger", "-f", temp_file, "balance"],
        capture_output=True,
        text=True,
        check=True,
    )

    with open(ledger_file, "a", encoding="utf-8") as file:
        if existing_content and not existing_content.endswith("\n"):
            file.write("\n")

        file.write("\n")
        file.write(transaction_content)
        file.write("\n")


def _get_transfer_destination(description: str) -> str:
    """
    Determines the destination account for an outgoing bank transfer.

    Add more account mappings here as needed.
    """
    description_lower = description.lower()

    if "st george" in description_lower:
        return "Assets:Bank:StGeorge Incentive Saver"

    if "netbank saver" in description_lower:
        return "Assets:Bank:CommBank NetBank Saver"

    if "commbank savings" in description_lower:
        return "Assets:Bank:CommBank Savings"

    return "Assets:Bank:Transfers"


def import_csv_transactions(
    csv_file: str,
    bank_account: str,
    currency: str = "AUD",
) -> str:
    """
    Imports transactions from a bank CSV into hledger files.

    Expected CSV structure:
        Column 1: Date in DD/MM/YYYY format
        Column 2: Transaction amount
        Column 3: Transaction description
        Column 4: Running account balance, ignored

    Categorisation rules:
        - Positive amount containing "Salary":
            INCOME_FILE using Income:Salary
        - Other positive amounts:
            INCOME_FILE using Income:Uncategorised
        - Negative amount containing "Transfer to":
            BANK_FILE using an Assets:Bank destination
        - Other negative amounts:
            EXPENSES_FILE using Expenses:Uncategorised
    """
    bank_temp_file = "temp_bank_csv_import.hledger"
    income_temp_file = "temp_income_csv_import.hledger"
    expense_temp_file = "temp_expense_csv_import.hledger"

    try:
        if not csv_file:
            return "Error: A CSV file path is required."

        if not bank_account:
            return "Error: A bank account is required."

        bank_account = _normalise_bank_account(bank_account)

        currency = (currency or "AUD").strip().upper()

        bank_transactions: list[str] = []
        income_transactions: list[str] = []
        expense_transactions: list[str] = []
        skipped_rows: list[str] = []

        with open(
            csv_file,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.reader(file)

            for row_number, row in enumerate(reader, start=1):
                if not row or all(not value.strip() for value in row):
                    continue

                if len(row) < 3:
                    skipped_rows.append(
                        f"Row {row_number}: expected at least 3 columns"
                    )
                    continue

                raw_date = row[0].strip()
                raw_amount = row[1].strip()
                description = row[2].strip()

                try:
                    date = datetime.strptime(
                        raw_date,
                        "%d/%m/%Y",
                    ).strftime("%Y-%m-%d")

                    cleaned_amount = (
                        raw_amount
                        .replace("$", "")
                        .replace(",", "")
                        .replace('"', "")
                        .strip()
                    )

                    amount = float(cleaned_amount)

                    if amount == 0:
                        skipped_rows.append(
                            f"Row {row_number}: zero-value transaction"
                        )
                        continue

                    if not description:
                        description = "Imported bank transaction"

                    description_lower = description.lower()

                    is_salary = (
                        amount > 0
                        and "salary" in description_lower
                    )

                    is_bank_transfer = (
                        amount < 0
                        and "transfer to" in description_lower
                    )

                    if is_salary:
                        transaction_string = (
                            f"{date} * {description}\n"
                            f"    {bank_account}    "
                            f"{amount:.2f} {currency}\n"
                            f"    Income:Salary    "
                            f"-{amount:.2f} {currency}"
                        )

                        income_transactions.append(transaction_string)

                    elif is_bank_transfer:
                        transfer_amount = abs(amount)

                        destination_account = _get_transfer_destination(
                            description
                        )

                        transaction_string = (
                            f"{date} * {description}\n"
                            f"    {destination_account}    "
                            f"{transfer_amount:.2f} {currency}\n"
                            f"    {bank_account}    "
                            f"-{transfer_amount:.2f} {currency}"
                        )

                        bank_transactions.append(transaction_string)

                    elif amount > 0:
                        transaction_string = (
                            f"{date} * {description}\n"
                            f"    {bank_account}    "
                            f"{amount:.2f} {currency}\n"
                            f"    Income:Uncategorised    "
                            f"-{amount:.2f} {currency}"
                        )

                        income_transactions.append(transaction_string)

                    else:
                        expense_amount = abs(amount)

                        transaction_string = (
                            f"{date} * {description}\n"
                            f"    Expenses:Uncategorised    "
                            f"{expense_amount:.2f} {currency}\n"
                            f"    {bank_account}    "
                            f"-{expense_amount:.2f} {currency}"
                        )

                        expense_transactions.append(transaction_string)

                except ValueError as error:
                    skipped_rows.append(
                        f"Row {row_number}: {error}"
                    )

        total_transactions = (
            len(bank_transactions)
            + len(income_transactions)
            + len(expense_transactions)
        )

        if total_transactions == 0:
            skipped_message = "; ".join(skipped_rows)

            return (
                "Error: No valid transactions were found in the CSV file."
                + (
                    f" Skipped rows: {skipped_message}"
                    if skipped_message
                    else ""
                )
            )

        _validate_and_append_transactions(
            ledger_file=BANK_FILE,
            transactions=bank_transactions,
            temp_file=bank_temp_file,
        )

        _validate_and_append_transactions(
            ledger_file=INCOME_FILE,
            transactions=income_transactions,
            temp_file=income_temp_file,
        )

        _validate_and_append_transactions(
            ledger_file=EXPENSES_FILE,
            transactions=expense_transactions,
            temp_file=expense_temp_file,
        )

        result = (
            f"Successfully imported {total_transactions} transactions. "
            f"{len(bank_transactions)} bank transfers were written to "
            f"BANK_FILE, "
            f"{len(income_transactions)} income transactions were written "
            f"to INCOME_FILE, and "
            f"{len(expense_transactions)} expense transactions were written "
            f"to EXPENSES_FILE."
        )

        if skipped_rows:
            result += (
                f" Skipped {len(skipped_rows)} rows: "
                + "; ".join(skipped_rows)
            )

        return result

    except FileNotFoundError as error:
        return f"Error: File not found. {error}"

    except PermissionError as error:
        return f"Error: Permission denied. {error}"

    except subprocess.CalledProcessError as error:
        error_message = (
            error.stderr.strip()
            or error.stdout.strip()
            or str(error)
        )

        return (
            "Error: The imported transactions failed "
            f"hledger validation. {error_message}"
        )

    except Exception as error:
        return f"Error: {type(error).__name__}: {error}"

    finally:
        for temp_file in [
            bank_temp_file,
            income_temp_file,
            expense_temp_file,
        ]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass