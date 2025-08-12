from langgraph.graph.message import AnyMessage, add_messages
# from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver
# from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
# from langgraph.checkpoint.sqlite import SqliteSaver  # 改用同步版本的 SqliteSaver
# from langgraph.checkpoint.memory import MemoryCheckpointer
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict
from typing import Annotated, Literal, Dict
from dotenv import load_dotenv
from pathlib import Path
import uuid
import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage

from tools import available_functions

load_dotenv()
model = os.getenv('LLM_MODEL', 'gpt-4o')

# Initialize memory
memory = MemorySaver()

tools = [tool for _, tool in available_functions.items()]
chatbot = ChatOpenAI(
            model=model,
            api_key=os.environ.get("openai_api_key"),
            base_url=os.environ.get("openai_api_base")
        )
chatbot_with_tools = chatbot.bind_tools(tools)

### State
class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        messages: List of chat messages.
    """
    messages: Annotated[list[AnyMessage], add_messages]

async def call_model(state: GraphState, config: RunnableConfig) -> Dict[str, AnyMessage]:
    """
    Function that calls the model to generate a response.

    Args:
        state (GraphState): The current graph state

    Returns:
        dict: The updated state with a new AI message
    """
    print("---CALL MODEL---")
    messages = state["messages"]

    # Invoke the chatbot with the binded tools
    response = await chatbot_with_tools.ainvoke(messages, config)
    print("Response from model:", response)

    # We return an object because this will get added to the existing list
    return {"messages": response}

def tool_node(state: GraphState) -> Dict[str, AnyMessage]:
    """
    Function that handles all tool calls.

    Args:
        state (GraphState): The current graph state

    Returns:
        dict: The updated state with tool messages
    """
    print("---TOOL NODE---")
    messages = state["messages"]
    last_message = messages[-1] if messages else None

    outputs = []

    if last_message and last_message.tool_calls:
        for call in last_message.tool_calls:
            tool = available_functions.get(call['name'], None)

            if tool is None:
                raise Exception(f"Tool '{call['name']}' not found.")

            output = tool.invoke(call['args'])
            outputs.append(ToolMessage(
                output if isinstance(output, str) else json.dumps(output), 
                tool_call_id=call['id']
            ))

    return {'messages': outputs}

def should_continue(state: GraphState) -> Literal["__end__", "tools"]:
    """
    Determine whether to continue or end the workflow based on if there are tool calls to make.

    Args:
        state (GraphState): The current graph state

    Returns:
        str: The next node to execute or END
    """
    print("---SHOULD CONTINUE---")
    messages = state["messages"]
    last_message = messages[-1] if messages else None

    # If there is no function call, then we finish
    if not last_message or not last_message.tool_calls:
        return END
    else:
        return "tools"

    
async def get_runnable():
    # Create data directory if it doesn't exist
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Use a file-based database instead of memory
    db_path = data_dir / f"chat_{uuid.uuid4()}.db"

    workflow = StateGraph(GraphState)

    # Define the nodes and how they connect
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue
    )
    workflow.add_edge("tools", "agent")

    # Use our simple checkpointer
    app = workflow.compile(checkpointer=memory)
    return app