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
