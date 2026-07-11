import sys
import os
from agents.portfolio_agent import PortfolioAgent

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def main():
    clear_screen()
    agent = PortfolioAgent()
    print("==========================================")
    print("   Portfolio Agent - Financial Assistant ")
    print("==========================================")
    print("I can help you:")
    print("  • View account balances and portfolio summaries")
    print("  • Search transactions")
    print("  • Record income, expenses and bank transfers")
    print("  • Import CommBank CSV statements")
    print()
    print("Available actions:")
    print("  - What's my current balance?")
    print("  - Show transactions for a specific account, (e.g. Assets:Bank:CommBank Every Day)")
    print("  - Add a new transaction (e.g., 'On 2026-07-10, spent 50 AUD on groceries from CommBank Every Day')")
    print("  - Add income (e.g., 'Add income of 1000 AUD for Salary')")
    print("  - Add an expense (e.g., 'Add expense of 50 AUD for groceries from CommBank Every Day')")
    print("  - Add a bank transfer (e.g., 'Transfer 100 AUD from Savings to Spending')")
    print("  - Import statement commbank_july.csv")
    print("==========================================")
    print("Type 'exit' or 'quit' to close the program.")
    
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            if not user_input.strip():
                continue
                
            response = agent.run(user_input)
            print(f"\nAssistant: {response}")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
