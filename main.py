from datetime import datetime


def handle_command(command: str) -> bool:
    """Processes a user command.
    
    Returns:
        bool: False if the loop should terminate ('exit'), True otherwise.
    """
    cleaned_command = command.strip().lower()

    if cleaned_command == "hello":
        print("Assistant: Hello! How can I help you today?")
    elif cleaned_command == "time":
        current_time = datetime.now().strftime("%I:%M %p")
        print(f"Assistant: The current time is {current_time}.")
    elif cleaned_command == "exit":
        print("Assistant: Goodbye!")
        return False
    else:
        print("Assistant: I don't understand that command yet.")

    return True


def main() -> None:
    """Main execution loop for the virtual assistant."""
    print("=== Voice Virtual Assistant (Text Mode) ===")
    print("Available commands: hello, time, exit\n")

    while True:
        try:
            user_input = input("You: ")
            # Ignore empty inputs
            if not user_input.strip():
                continue

            should_continue = handle_command(user_input)
            if not should_continue:
                break
        except (KeyboardInterrupt, EOFError):
            print("\nAssistant: Goodbye!")
            break


if __name__ == "__main__":
    main()
