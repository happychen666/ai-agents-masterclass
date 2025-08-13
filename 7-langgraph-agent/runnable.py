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
import cv2
import numpy as np

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
    print("Last message===", last_message)
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
    graph = workflow.compile(checkpointer=memory)

    # Save Graph Flowchart
    # Save Graph Flowchart with proper path handling
    current_dir = Path(__file__).parent
    assets_dir = current_dir / "assets"
    
    print(f"Current directory: {current_dir}")
    print(f"Assets directory: {assets_dir}")
    
    # Create assets directory if it doesn't exist
    assets_dir.mkdir(exist_ok=True)
    
    # Use absolute path for saving
    output_path = str(assets_dir / "graph2.png")
    print(f"Output path: {output_path}")
    
    try:
        # Get graph visualization
        image_bytes = graph.get_graph().draw_mermaid_png()
        if image_bytes is None:
            print("Error: No image data generated")
            return graph
            
        print(f'Image bytes length: {len(image_bytes)}')
        
        # Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        if len(nparr) == 0:
            print("Error: Empty image data")
            return graph
            
        decoded = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if decoded is None:
            print("Error: Failed to decode image")
            return graph
        
        # Save with normalized path and check if directory exists
        assets_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(assets_dir.resolve() / "graph2.png")
        
        # Try alternative saving method if cv2.imwrite fails
        try:
            success = cv2.imwrite(output_path, decoded)
            if not success:
                # Try direct file writing
                with open(output_path, 'wb') as f:
                    f.write(cv2.imencode('.png', decoded)[1].tobytes())
                print(f"Graph flowchart saved using alternative method at: {output_path}")
            else:
                print(f"Graph flowchart successfully saved at: {output_path}")
        except Exception as write_error:
            print(f"Error saving image: {write_error}")
            
    except Exception as e:
        print(f"Error in image processing/saving: {str(e)}")
        import traceback
        traceback.print_exc()

    return graph

# Test the function directly
if __name__ == "__main__":
    import asyncio
    
    print("Starting graph generation...")
    try:
        asyncio.run(get_runnable())
        print("Process completed")
    except Exception as e:
        print(f"Main execution error: {str(e)}")
        import traceback
        traceback.print_exc()