import sys
from agents.portfolio_agent import PortfolioAgent

def main():
    agent = PortfolioAgent()
    print("==========================================")
    print("   Portfolio Agent - Financial Assistant ")
    print("==========================================")
    print("Available actions:")
    print("  - Get your current balance")
    print("  - Get a summary of your portfolio")
    print("  - Get transactions for a specific account")
    print("  - Add a new transaction (e.g., 'On 2026-07-10, spent 50 AUD on groceries from CommBank Every Day')")
    print("  - Add income (e.g., 'Add income of 1000 AUD for Salary')")
    print("  - Add an expense (e.g., 'Add expense of 50 AUD for groceries from CommBank Every Day')")
    print("  - Add a bank transfer (e.g., 'Transfer 100 AUD from Savings to Spending')")
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
