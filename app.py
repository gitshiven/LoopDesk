import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from agent.graph import run_ticket
from memory.corrections import save_correction, load_corrections

st.set_page_config(page_title="LoopDesk", page_icon="↺", layout="wide")

# Styling
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
    .billing  { background: #fff3e0; color: #e65100; }
    .technical { background: #e3f2fd; color: #0d47a1; }
    .general  { background: #e8f5e9; color: #1b5e20; }
    .escalated { background: #fce4ec; color: #880e4f; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("# ↺ LoopDesk")
st.markdown("*AI support triage — resolving tickets intelligently*")
st.divider()

# Tabs
tab1, tab2 = st.tabs(["🎫 Customer", "🔍 Reviewer Dashboard"])

# ── TAB 1: CUSTOMER ──────────────────────────────────────
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

            # Store result in session for reviewer
            if "tickets" not in st.session_state:
                st.session_state.tickets = []
            st.session_state.tickets.append(result)

            st.divider()

            # Category badge
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

# ── TAB 2: REVIEWER DASHBOARD ────────────────────────────
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