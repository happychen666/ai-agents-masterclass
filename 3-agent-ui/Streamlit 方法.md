    st.title("Asana Chatbot")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content=f"You are a personal assistant who helps manage tasks in Asana. The current date is: {datetime.now().date()}")
        ]    

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        message_json = json.loads(message.model_dump_json())
        message_type = message_json["type"]
        if message_type in ["human", "ai", "system"]:
            with st.chat_message(message_type):
                st.markdown(message_json["content"])        

    # React to user input
    if prompt := st.chat_input("What would you like to do today?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append(HumanMessage(content=prompt))

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            stream = prompt_ai(st.session_state.messages)
            response = st.write_stream(stream)
        
        st.session_state.messages.append(AIMessage(content=response))

解释这段代码的含义和作用，我对sreamlit不熟悉，请把代码中使用的streamlit方法也解释以下

我给你拆开讲，这段代码是一个 **基于 Streamlit 的简单 Asana 聊天机器人界面**，它做了三件事：

1. **显示标题和历史消息**
2. **等待用户输入**
3. **调用 AI 生成回复并显示**

我会先讲 **每行代码的作用**，再顺带解释用到的 **Streamlit 方法**（st.title、st.session\_state、st.chat\_message、st.chat\_input、st.markdown、st.write\_stream 等）。

---

## 逐行解释

```python
st.title("Asana Chatbot")
```

* **作用**：在页面上显示一个大标题 `"Asana Chatbot"`。
* **Streamlit 方法解释**：

  * `st.title(text)` 会渲染为网页上的一级标题（大字体）。
  * 类似 HTML 里的 `<h1>` 标签。

---

```python
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content=f"You are a personal assistant who helps manage tasks in Asana. The current date is: {datetime.now().date()}")
    ]    
```

* **作用**：初始化聊天历史。
* **逻辑**：

  * `st.session_state` 是 **Streamlit 的会话状态存储**（类似一个持久化字典，页面刷新不会丢失数据）。
  * 检查 `"messages"` 是否已经存在，不存在就创建，并放入一条系统消息（`SystemMessage`，告诉 AI 它的角色和当前日期）。
* **好处**：保证第一次加载页面时有一条系统指令，之后用户发消息会追加到这个列表。

---

```python
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    message_json = json.loads(message.model_dump_json())
    message_type = message_json["type"]
    if message_type in ["human", "ai", "system"]:
        with st.chat_message(message_type):
            st.markdown(message_json["content"])
```

* **作用**：把所有历史聊天记录显示出来。
* **逻辑**：

  1. 遍历 `st.session_state.messages` 里的每条消息。
  2. `message.json()` → 把消息转成 JSON 格式的字符串。
  3. `json.loads(...)` → 解析成 Python 字典。
  4. 从中取出 `type`（消息类型）和 `content`（消息内容）。
  5. 如果 `type` 是 `"human"`（用户）、`"ai"`（助手）、`"system"`（系统），就显示出来。
  6. `with st.chat_message(message_type):`

     * 在 Streamlit 聊天界面创建一个气泡（根据 `message_type` 会有不同样式，比如用户右对齐，AI 左对齐）。
  7. `st.markdown(message_json["content"])` → 用 Markdown 格式渲染消息内容。

---

```python
# React to user input
if prompt := st.chat_input("What would you like to do today?"):
```

* **作用**：显示一个聊天输入框，等待用户输入。
* **Streamlit 方法解释**：

  * `st.chat_input(placeholder)` 会渲染一个聊天输入框。
  * 用户按回车后返回输入的字符串（如果为空则返回 `None`）。
  * 这里用了 **海象运算符** `:=`，即一边接收输入，一边赋值给 `prompt`。

---

```python
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
```

* **作用**：即时显示用户刚刚输入的内容（右侧气泡）。
* **Streamlit 方法解释**：

  * `st.chat_message(role)` → 开启一个聊天气泡（`role` 可以是 `"user"`, `"assistant"`, `"system"`）。
  * `.markdown(prompt)` → 用 Markdown 渲染内容。

---

```python
    # Add user message to chat history
    st.session_state.messages.append(HumanMessage(content=prompt))
```

* **作用**：把用户输入存进聊天历史（后续 AI 生成回复时要用）。

---

```python
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        stream = prompt_ai(st.session_state.messages)
        response = st.write_stream(stream)
```

* **作用**：

  * `with st.chat_message("assistant"):` → 创建一个 AI 回复气泡。
  * `stream = prompt_ai(st.session_state.messages)` → 调用你写的 `prompt_ai` 方法，把所有聊天历史传过去，让 AI 生成一个回复流（**流式输出**）。
  * `st.write_stream(stream)` → 边生成边显示（就像 ChatGPT 那样一边打字一边输出）。

    * **`st.write_stream`** 是 Streamlit 新 API，可以接收一个生成器/迭代器，每次 yield 一段文本，就实时更新界面。
    * 返回值 `response` 会是整个合并好的文本。

---

```python
    st.session_state.messages.append(AIMessage(content=response))
```

* **作用**：把 AI 回复加入聊天历史，保证刷新页面后还能看到。

---

## Streamlit 主要方法总结表

| 方法                           | 作用          | 举例                                                |
| ---------------------------- | ----------- | ------------------------------------------------- |
| `st.title(text)`             | 显示大标题       | `st.title("My App")`                              |
| `st.session_state`           | 会话持久存储（跨刷新） | `st.session_state.count = 0`                      |
| `st.chat_message(role)`      | 聊天气泡容器      | `with st.chat_message("user"): st.write("Hello")` |
| `.markdown(text)`            | Markdown 渲染 | `.markdown("**Bold** text")`                      |
| `st.chat_input(placeholder)` | 聊天输入框       | `msg = st.chat_input("Say hi")`                   |
| `st.write_stream(stream)`    | 流式输出        | `st.write_stream(my_generator())`                 |

---

如果你愿意，我可以帮你画一个 **交互流程图**，把“用户输入 → 存储 → 调用 AI → 流式输出 → 更新历史”整个过程画出来，你会更直观地看懂这段代码。这样即使你不熟悉 Streamlit，也能快速搭建类似的聊天界面。

你要我帮你画吗？这样会特别直观。

---

with st.chat_message(message_type):

在 Streamlit 聊天界面创建一个气泡（根据 message_type 会有不同样式，比如用户右对齐，AI 左对齐）。

这个左右对齐是在哪里控制的

这个左右对齐 **不是你代码里写的**，而是 **Streamlit 自己在 `st.chat_message()` 组件内部做的样式控制**。

具体来说：

* `st.chat_message(role)` 里传入的 **`role`**（比如 `"user"`、`"assistant"`、`"system"`, 甚至自定义 `"human"`、`"ai"`）会告诉 Streamlit 这条消息是谁发的。
* Streamlit 内部的前端 CSS（React 组件）会根据这个 `role` 来套不同的样式：

  * `"user"` → 右对齐（常见的聊天 UI，用户在右侧）
  * `"assistant"` / `"system"` → 左对齐（AI 或系统消息在左侧）
  * 头像、气泡颜色、背景色等也会跟着改变
* 这些样式是 **Streamlit 的前端代码内置**的，你不用自己写 CSS。

---

### 举例说明

如果你写：

```python
with st.chat_message("user"):
    st.write("Hello from user!")

with st.chat_message("assistant"):
    st.write("Hello from AI!")
```

你会看到：

* 第一条 **右边气泡**（颜色一般更亮）
* 第二条 **左边气泡**（颜色一般偏灰）

---

### 如果你想改左右对齐

* **方法 1（官方 API 支持有限）**：目前官方只通过 `role` 自动控制，不能直接改成“用户也在左边”这种。
* **方法 2（CSS Hack）**：你可以用 `st.markdown` 注入自定义 CSS 来覆盖 Streamlit 默认样式，比如：

```python
st.markdown("""
<style>
[data-testid="stChatMessage"][data-testid="user"] {
    justify-content: flex-start !important; /* 改成左对齐 */
}
</style>
""", unsafe_allow_html=True)
```

* 不过这种方法依赖内部 DOM 结构，Streamlit 升级后可能失效。

---

我可以帮你把 **Streamlit 内部 `st.chat_message` 的 role → 样式映射表**画出来，这样你就清楚为什么它会左右对齐了。
要帮你画吗？这样你能直接看懂它的规则。
