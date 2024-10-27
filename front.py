import streamlit as st
from llm import run_qna, run_tool_qna, execute_tool, identify_tool, get_tool_call


# states
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Oi, me chamo Rampo, um assistente virtual. Em que posso te ajudar hoje?",
        }
    ]

if "loading" not in st.session_state:
    st.session_state.loading = False

# callbacks
def on_submit():
    st.session_state.loading = True

# design
st.title("Rampo Chat")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_prompt = st.chat_input(placeholder="Olá, Rampo", disabled=st.session_state.loading, on_submit=on_submit)

if not user_prompt:
    st.stop()

# draw the user message on the screen
with st.chat_message("user"):
    st.markdown(user_prompt)

# add the user message to the messages list
st.session_state.messages.append({"role": "user", "content": user_prompt})

# get the chat response
if "@tools" not in user_prompt:
    user_prompt.replace("@tools", "")
    answer = run_qna(user_prompt)
else:
    tool_call = get_tool_call(user_prompt)
    tool = identify_tool(tool_call)

    # show user more info
    with st.chat_message("assistant"):
        tool_msg = f"__TOOL:__ Vou usar o seguinte comando: {tool_call['name']} com os seguintes argumentos: {tool_call['args']}."
        st.markdown(tool_msg)
        st.session_state.messages.append({"role": "assistant", "content": tool_msg})

    tool_result = execute_tool(tool, tool_call)
    answer = run_tool_qna(
        question=user_prompt,
        tool_name=tool.name,
        tool_description=tool.description,
        tool_arguments=tool_call["args"],
        tool_result=tool_result,
    )

with st.chat_message("assistant"):
    st.markdown(answer)

# add the assistant message to the messages list
st.session_state.messages.append({"role": "assistant", "content": answer})
st.session_state.loading = False
st.rerun()