from langchain_core.messages import HumanMessage
from langgraph.types import Command
from tools.loan_statement_tool import get_loan_statement
from datetime import datetime

def test_direct_tool():
    # Simulated state
    state = {
        "messages": [
            HumanMessage(content="Please provide my loan statement for last month"),
        ]
    }

    # Call the tool properly using .invoke()
    command: Command = get_loan_statement.invoke({
        "customer_id": "565343",
        "tool_call_id": "test_call_001",
        "state": state
    })

    print("\n--- Tool Output ---")
    for msg in command.update["messages"]:
        print(msg.content)

if __name__ == "__main__":
    test_direct_tool()
