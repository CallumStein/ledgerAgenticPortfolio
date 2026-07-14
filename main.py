import os

import asyncio
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import HSplit, Layout, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.styles import Style

from agents.portfolio_agent import PortfolioAgent



def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def main() -> None:
    clear_screen()

    style = Style.from_dict({
    "conversation": "fg:#d0d0d0",
    "prompt": "fg:#00d7d7 bold",
    "input": "fg:#ffffff",
    "footer": "fg:#808080",
    "separator": "fg:#555555",
    })

    agent = PortfolioAgent()

    conversation = TextArea(
        text=(
            "Portfolio Agent - Financial Assistant\n"
            "=====================================\n\n"
            "I can help you:\n"
            "  • View balances and portfolio summaries\n"
            "  • Search transactions\n"
            "  • Record income, expenses and bank transfers\n"
            "  • Import CommBank CSV statements\n\n"
            "Examples:\n"
            "  • What's my current balance?\n"
            "  • Show transactions for Assets:Bank:CommBank Every Day\n"
            "  • Add income of 1000 AUD for Salary\n"
            "  • Add expense of 50 AUD for groceries\n"
            "  • Transfer 100 AUD from Savings to Spending\n"
            "  • Import statement commbank_july.csv\n\n"
            "Type 'exit' or 'quit' to close.\n"
        ),
        read_only=True,
        scrollbar=True,
        focusable=False,
        wrap_lines=True,
        style="class:conversation",
    )

    input_area = TextArea(
        height=3,
        prompt=[("class:prompt", "❯ "),],
        multiline=False,
        wrap_lines=False,
        style="class:input",
    )

    separator = Window(
        height=1,
        char="─",
        style="class:separator",
    )

    footer = Window(
        height=1,
        content=FormattedTextControl([("class:footer", " Enter: send  |  Type 'exit' or 'quit' to close. "),]),
    )

    root_container = HSplit(
        [
            conversation,
            separator,
            input_area,
            separator,
            Window(height=1),
            footer,
        ]
    )

    application = Application(
        layout=Layout(
            root_container,
            focused_element=input_area,
        ),
        full_screen=True,
        mouse_support=True,
        style=style,
        #color_depth=None,
    )

    def append_message(role: str, message: str) -> None:
        current_text = conversation.text

        if current_text and not current_text.endswith("\n"):
            current_text += "\n"

        conversation.text = (
            current_text
            + f"\n{role}:\n{message}\n"
        )

        conversation.buffer.cursor_position = len(
            conversation.buffer.text
        )

        application.invalidate()

    async def process_prompt(user_input: str) -> None:
        """
        Run the blocking agent call outside the UI thread.
        """
        try:
            response = await asyncio.to_thread(
                agent.run,
                user_input,
            )

            marker = "\nAssistant:\nThinking...\n"

            if conversation.text.endswith(marker):
                conversation.text = conversation.text[
                    :-len(marker)
                ]

            append_message("Assistant", response)

        except Exception as error:
            marker = "\nAssistant:\nThinking...\n"

            if conversation.text.endswith(marker):
                conversation.text = conversation.text[
                    :-len(marker)
                ]

            append_message(
                "Error",
                f"{type(error).__name__}: {error}",
            )

        finally:
            input_area.read_only = False
            application.layout.focus(input_area)
            application.invalidate()


    def submit_input(buffer: Buffer) -> bool:
        user_input = buffer.text.strip()
        buffer.text = ""

        if not user_input:
            return True

        if user_input.lower() in {"exit", "quit"}:
            application.exit()
            return True

        # These messages are added immediately.
        append_message("You", user_input)
        append_message("Assistant", "Thinking...")

        # Prevent another submission while the current request is running.
        input_area.read_only = True

        # Force prompt_toolkit to redraw before starting the model request.
        application.invalidate()

        # Run the blocking request in the background.
        application.create_background_task(
            process_prompt(user_input)
        )

        return True

    input_area.buffer.accept_handler = submit_input

    try:
        application.run()
    except KeyboardInterrupt:
        pass

    print("Goodbye!")


if __name__ == "__main__":
    main()