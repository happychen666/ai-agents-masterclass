import streamlit as st
import pandas as pd
import numpy as np

# 1. 页面标题
st.title("📊 Streamlit Demo")
st.write("这是一个简单的 Streamlit 示例，展示输入、输出和图表。")

# 2. 输入框
name = st.text_input("请输入你的名字：")
age = st.number_input("请输入你的年龄：", min_value=0, max_value=120, value=18)

# 3. 按钮交互
if st.button("提交"):
    st.success(f"你好，{name}！你今年 {age} 岁。")

# 4. 表格数据
data = pd.DataFrame({
    "A列": np.random.randint(0, 100, 5),
    "B列": np.random.rand(5)
})
st.subheader("📋 数据表格")
st.table(data)

# 5. 折线图
st.subheader("📈 折线图示例")
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=["X", "Y", "Z"]
)
st.line_chart(chart_data)

# 6. 上传文件
uploaded_file = st.file_uploader("上传 CSV 文件")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("文件内容：", df)
