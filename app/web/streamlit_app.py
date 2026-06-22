import os
from uuid import uuid4

import requests
import streamlit as st

from app.models import GetMessageRequestModel, IncomingMessage

DEFAULT_BOT_URL = os.getenv("ECHO_BOT_URL", "http://localhost:8000")
st.set_page_config(initial_sidebar_state="collapsed")

st.markdown("# YouAreBot - LLM Chat 🧠")
st.sidebar.markdown("# YouAreBot 🧠")

if "dialog_id" not in st.session_state:
    st.session_state.dialog_id = str(uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Type something"}]

if "metrics" not in st.session_state:
    st.session_state.metrics = {
        "total": 0,
        "participant_0_sum": 0.0,
        "participant_0_count": 0,
        "participant_1_sum": 0.0,
        "participant_1_count": 0,
        "correct_pairs": 0,
        "total_pairs": 0,
    }

with st.sidebar:
    if st.button("Reset"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.dialog_id = str(uuid4())

    bot_url = st.text_input("Bot URL", value=DEFAULT_BOT_URL, disabled=True)
    st.text_input("Dialog ID", value=st.session_state.dialog_id, disabled=True)

    st.markdown("### Metrics")
    m = st.session_state.metrics
    st.metric("Total predictions", m["total"])
    if m["participant_0_count"]:
        st.metric(
            "Avg user (p0) prob",
            f"{m['participant_0_sum'] / m['participant_0_count']:.1%}",
        )
    if m["participant_1_count"]:
        st.metric(
            "Avg bot reply prob",
            f"{m['participant_1_sum'] / m['participant_1_count']:.1%}",
        )
    if m["total_pairs"]:
        st.metric(
            "Pairs (reply > user)",
            f"{m['correct_pairs']} / {m['total_pairs']}",
        )


def classify(text: str, participant_index: int, msg_id: str) -> float | None:
    try:
        resp = requests.post(
            f"{bot_url}/predict",
            json=IncomingMessage(
                text=text,
                dialog_id=st.session_state.dialog_id,
                id=msg_id,
                participant_index=participant_index,
            ).model_dump(mode="json"),
            timeout=30,
        )
        if resp.ok:
            return resp.json()["is_bot_probability"]
    except requests.RequestException:
        pass
    return None


def render_message(msg):
    content = msg["content"]
    if msg.get("probability") is not None:
        p = msg["probability"]
        badge = "🤖" if p > 0.5 else "🧑"
        content = f"{content}  \n{badge} {p:.1%}"
    st.chat_message(msg["role"]).write(content)


for msg in st.session_state.messages:
    render_message(msg)

if prompt := st.chat_input():
    user_id = str(uuid4())
    user_prob = classify(prompt, 0, user_id)

    user_entry = {"role": "user", "content": prompt, "probability": user_prob}
    st.session_state.messages.append(user_entry)
    render_message(user_entry)

    if user_prob is not None:
        st.session_state.metrics["total"] += 1
        st.session_state.metrics["participant_0_sum"] += user_prob
        st.session_state.metrics["participant_0_count"] += 1

    resp = requests.post(
        f"{bot_url}/get_message",
        json=GetMessageRequestModel(
            dialog_id=st.session_state.dialog_id,
            last_msg_text=prompt,
            last_message_id=user_id,
        ).model_dump(mode="json"),
    )
    data = resp.json()
    reply_text = data["new_msg_text"]
    reply_prob = data.get("is_bot_probability")

    reply_entry = {
        "role": "assistant",
        "content": reply_text,
        "probability": reply_prob,
    }
    st.session_state.messages.append(reply_entry)
    render_message(reply_entry)

    if reply_prob is not None:
        st.session_state.metrics["total"] += 1
        st.session_state.metrics["participant_1_sum"] += reply_prob
        st.session_state.metrics["participant_1_count"] += 1

        if user_prob is not None:
            st.session_state.metrics["total_pairs"] += 1
            if reply_prob > user_prob:
                st.session_state.metrics["correct_pairs"] += 1

    st.rerun()
