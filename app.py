import streamlit as st
from openai import OpenAI

# 设置页面标题和布局
st.set_page_config(page_title="FinTech 财报小助手", page_icon="📈", layout="centered")

st.title("📈 FinTech 财报小助手")
st.caption("基于 DeepSeek 大模型构建的智能金融问答助手 | 深大金融科技作品")

# 尝试从 Streamlit 的 Secrets 中获取 API Key，如果没有则提示
try:
    api_key = st.secrets["DEEPSEEK_API_KEY"]
except:
    st.error("⚠️ 还没有配置 API Key 哦！请在 Streamlit 后台的 Settings -> Secrets 中填入：DEEPSEEK_API_KEY = '你的key'")
    st.stop()

# 初始化 DeepSeek 客户端 (DeepSeek 兼容 OpenAI 的接口)
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# 初始化聊天记录（如果没有的话）
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "你是一位资深的金融分析师，专攻财报解读。请用通俗易懂的语言回答用户的问题。绝对禁止提供具体的买入/卖出投资建议，且如果不知道答案，请直接回答不知道，严禁编造数据。"}
    ]

# 展示历史聊天记录
for message in st.session_state.messages:
    if message["role"] != "system": # 不展示系统提示词
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 用户输入框
if prompt := st.chat_input("请提问，例如：帮我总结一下这家公司的三大风险点。"):
    # 1. 把用户输入加入聊天记录并展示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 调用大模型生成回答
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            # 发起流式请求（打字机效果）
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=st.session_state.messages,
                stream=True
            )
            # 逐字显示
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
            # 把 AI 回答加入聊天记录
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"出错了，请检查你的 API Key 或网络。错误信息：{e}")
