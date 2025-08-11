整个 agent 的工作流如下：

用户输入：用户在 Streamlit 网页输入需求（如“创建一个任务”）。
消息历史维护：输入被加入 st.session_state.messages，包括系统消息、用户消息等。
AI 推理：prompt_ai(messages) 被调用，将消息历史传递给大模型（LLM）。
工具调用：LLM 判断是否需要调用工具（如创建任务），如果需要，会自动调用相应的 Python 函数，并将结果加入消息流。
多轮交互：如果 LLM 需要多次工具调用，会递归调用 prompt_ai，直到得到最终回复。
结果展示：AI 的回复通过 Streamlit 实时展示给用户，并加入消息历史。
如何直接看到 LLM 的数据？
你可以通过打印或展示 messages 参数，来直接看到 LLM 处理的所有上下文数据。
例如，在 prompt_ai 函数开头加一行：

这样每次调用 LLM 前，都会在控制台输出当前 LLM 能看到的所有消息（包括系统、用户、AI、工具消息等）。

总结：
只需在 prompt_ai 里打印 messages，即可直接看到 LLM 的全部上下文数据。