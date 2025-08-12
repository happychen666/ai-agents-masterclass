好，那我直接帮你做一个**Streamlit + ChatGPT 聊天机器人**的完整可运行示例，
你跑完这个，就能在浏览器里用网页和大模型对话了。

---

## **1. 功能说明**

* 左侧输入 OpenAI API Key（安全起见，不写死在代码里）
* 中间聊天窗口使用 `st.chat_message` 显示对话
* 输入框使用 `st.chat_input`
* 聊天记录存在 `st.session_state`，刷新页面不丢失
* 兼容 GPT-4o / GPT-4 / GPT-3.5

---

## **2. 完整代码**

保存成 `chatbot.py`：

```python
import streamlit as st
from openai import OpenAI

# ===== 1. 页面标题 =====
st.set_page_config(page_title="💬 ChatGPT Web", page_icon="🤖")
st.title("💬 ChatGPT 网页版 Demo")

# ===== 2. 左侧 API Key 输入 =====
with st.sidebar:
    st.header("🔑 API 设置")
    api_key = st.text_input("请输入 OpenAI API Key：", type="password")
    st.markdown("[获取 API Key](https://platform.openai.com/account/api-keys)")

# ===== 3. 初始化聊天记录 =====
if "messages" not in st.session_state:
    st.session_state.messages = []

# ===== 4. 显示历史对话 =====
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ===== 5. 用户输入 =====
if prompt := st.chat_input("请输入你的问题..."):
    # 显示用户输入
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if not api_key:
        st.error("请先在左侧输入 API Key！")
    else:
        try:
            # ===== 6. 调用 OpenAI API =====
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # 你也可以改成 gpt-4 / gpt-3.5-turbo
                messages=st.session_state.messages,
                temperature=0.7
            )
            reply = response.choices[0].message.content

            # 显示助手回复
            with st.chat_message("assistant"):
                st.markdown(reply)

            # 保存到会话
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"调用 API 出错：{e}")
```

---

## **3. 安装依赖**

```bash
pip install streamlit openai
```

---

## **4. 运行**

```bash
streamlit run chatbot.py
```

浏览器会自动打开 `http://localhost:8501`
左侧输入你的 **OpenAI API Key**，然后就能和 GPT 对话了。

---

## **5. 运行效果**

* **界面结构**

  * 左侧栏：API Key 输入
  * 主区域：聊天记录（气泡样式）
  * 下方：输入框
* **交互**

  * 用户输入消息 → 立刻显示在右侧
  * GPT 回复 → 自动显示在左侧
  * 刷新页面不会丢历史（存在 `st.session_state`）

---

💡 **可选优化**

* 记忆上下文长度（自动丢掉旧消息防止 token 超限）
* 加上**文件上传**，让 GPT 根据你上传的文档回答问题
* 加上**语音输入 + 语音播报**，做成语音 AI 助手
* 加上**模型选择**下拉框（切换 GPT-4 / GPT-3.5）

---

如果你愿意，我可以帮你升级这个例子，让它**支持文件上传 + 让 GPT 读取文件内容回答问题**，这样就能做一个**简易 RAG 知识问答系统**。
你要我帮你加这个功能吗？这样就能直接用它来做医疗、技术、合同解读等场景的 AI 助手。
