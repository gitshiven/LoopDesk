import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

if not os.path.exists("chroma_db"):
    from rag.retriever import build_vectorstore
    build_vectorstore()

from agent.graph import run_ticket
from memory.corrections import save_correction, load_corrections

st.set_page_config(page_title="LoopDesk", page_icon="↺", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Ubuntu:wght@300;400;500;700&display=swap');
    * { font-family: 'Ubuntu', sans-serif; }
    .block-container { padding-top: 2rem; }
    .category-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .billing   { background: #fff3e0; color: #e65100; }
    .technical { background: #e3f2fd; color: #0d47a1; }
    .general   { background: #e8f5e9; color: #1b5e20; }
    .escalated { background: #fce4ec; color: #880e4f; }
</style>
""", unsafe_allow_html=True)

# Demo banner
st.markdown("""
<div style="
    background: linear-gradient(90deg, #1a0a00, #2a1000);
    border: 1px solid #ff3c00;
    border-radius: 6px;
    padding: 14px 20px;
    margin-bottom: 20px;
">
    <div style="color: #ff3c00; font-size: 0.7rem; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 6px;">
        ⚡ Live Demo
    </div>
    <div style="color: #f2efe8; font-size: 0.85rem; line-height: 1.6;">
        This is a demo instance of <strong>LoopDesk</strong>, running on self-curated documents 
        for a fictional company called <strong>NovaPay</strong> — a payments platform. The AI 
        has been trained to triage NovaPay support tickets across billing, technical, and general categories.
    </div>
    <div style="color: #999; font-size: 0.75rem; margin-top: 10px; line-height: 1.6;">
        💼 <strong style="color:#f2efe8">Want this for your business?</strong> 
        We replace the NovaPay documents with your company's knowledge base — your policies, 
        your FAQs, your tone. The agent learns your business in minutes.
        <br/>Contact: <span style="color:#ff3c00">ss.shiven44@gmail.com</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("# ↺ LoopDesk")
st.markdown("*AI support triage — resolving tickets intelligently*")
st.divider()

tab1, tab2 = st.tabs(["🎫 Customer", "🔍 Reviewer Dashboard"])

with tab1:
    st.subheader("Submit a Support Ticket")
    message = st.text_area(
        "Describe your issue",
        placeholder="e.g. I was charged twice this month...",
        height=120
    )

    if st.button("Submit Ticket", type="primary"):
        if not message.strip():
            st.warning("Please enter a message.")
        else:
            with st.spinner("Agent is thinking..."):
                result = run_ticket(message)

            if "tickets" not in st.session_state:
                st.session_state.tickets = []
            st.session_state.tickets.append(result)

            st.divider()

            cat = result["category"]
            escalated = result["escalated"]
            badge_class = "escalated" if escalated else cat

            st.markdown(f"""
                <span class="category-badge {badge_class}">
                    {"⚠ ESCALATED" if escalated else cat.upper()}
                </span>
            """, unsafe_allow_html=True)

            st.markdown(f"**Confidence Score:** {result['confidence']:.0%}")
            st.divider()

            if escalated:
                st.error("⚠ This ticket has been escalated to a human reviewer.")
                st.markdown("**Escalation Summary:**")
                st.code(result["escalation_summary"])
            else:
                st.success("✅ Auto-resolved")
                st.markdown("**Agent Response:**")
                st.info(result["response"])

with tab2:
    st.subheader("Reviewer Dashboard")
    st.caption("Review agent decisions and submit corrections to improve accuracy.")

    corrections = load_corrections()
    st.metric("Total Corrections Logged", len(corrections))
    st.divider()

    if "tickets" not in st.session_state or not st.session_state.tickets:
        st.info("No tickets submitted yet in this session. Submit one in the Customer tab.")
    else:
        for i, ticket in enumerate(reversed(st.session_state.tickets)):
            with st.expander(f"Ticket #{len(st.session_state.tickets) - i} — {ticket['category'].upper()} — {'⚠ Escalated' if ticket['escalated'] else '✅ Resolved'}"):
                st.markdown(f"**Message:** {ticket['message']}")
                st.markdown(f"**Category:** {ticket['category']}")
                st.markdown(f"**Confidence:** {ticket['confidence']:.0%}")
                st.markdown(f"**Response:** {ticket['response']}")

                st.divider()
                st.markdown("**Was this correct?**")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Correct", key=f"correct_{i}"):
                        st.success("Marked as correct.")
                with col2:
                    if st.button(f"❌ Wrong", key=f"wrong_{i}"):
                        st.session_state[f"show_correction_{i}"] = True

                if st.session_state.get(f"show_correction_{i}"):
                    correct_cat = st.selectbox(
                        "Correct category",
                        ["billing", "technical", "general"],
                        key=f"cat_{i}"
                    )
                    note = st.text_input("Note (optional)", key=f"note_{i}")
                    if st.button("Submit Correction", key=f"submit_{i}"):
                        save_correction(
                            message=ticket["message"],
                            wrong_category=ticket["category"],
                            correct_category=correct_cat,
                            note=note
                        )
                        st.success(f"Correction saved. Agent will learn from this.")
                        st.session_state[f"show_correction_{i}"] = False