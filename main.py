import sys
from agents.portfolio_agent import PortfolioAgent

def main():
    agent = PortfolioAgent()
    print("==========================================")
    print("   Portfolio Agent - Financial Assistant ")
    print("==========================================")
    print("Available actions:")
    print("  - Get your current balance")
    print("  - Get transactions for a specific account")
    print("  - Get a summary of your portfolio")
    print("  - Add a new transaction (e.g., 'On 10/7/2026, spent 50 AUD on groceries from CommBank Every Day')")
    print("  - Add income (e.g., 'Add 1000 AUD for Salary')")
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
