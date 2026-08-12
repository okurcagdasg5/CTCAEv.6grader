from pathlib import Path
import sqlite3
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "data" / "ctcae_v6.db"

st.set_page_config(
    page_title="CTCAE v6.0 Grader",
    page_icon="🧪",
    layout="centered",
)

st.markdown("""
<style>
.block-container {max-width: 980px; padding-top: 2rem;}
.result-card {
    border: 1px solid rgba(128,128,128,.30);
    border-radius: 16px;
    padding: 22px;
    margin-top: 12px;
}
.grade-number {
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: .2rem;
}
.small-muted {
    opacity: .70;
    font-size: .92rem;
}
</style>
""", unsafe_allow_html=True)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@st.cache_data
def load_socs():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT soc FROM ctcae ORDER BY soc"
        ).fetchall()
    return [r["soc"] for r in rows]

@st.cache_data
def load_terms(soc=None):
    with get_connection() as conn:
        if soc and soc != "All categories":
            rows = conn.execute(
                "SELECT term FROM ctcae WHERE soc=? ORDER BY term", (soc,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT term FROM ctcae ORDER BY term"
            ).fetchall()
    return [r["term"] for r in rows]

@st.cache_data
def get_ae(term):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM ctcae WHERE term=?", (term,)
        ).fetchone()
    return dict(row) if row else None

st.title("CTCAE v6.0 Grader")
st.caption("NCI Common Terminology Criteria for Adverse Events — v6.0 / MedDRA 28.0")

if not DB_PATH.exists():
    st.error("CTCAE database was not found.")
    st.stop()

soc_options = ["All categories"] + load_socs()
selected_soc = st.selectbox(
    "Category (SOC)",
    soc_options,
    help="Optional: narrow the list by CTCAE System Organ Class."
)

terms = load_terms(selected_soc)
selected_term = st.selectbox(
    "Adverse Event",
    options=terms,
    index=None,
    placeholder="Type to search for an adverse event…"
)

if selected_term:
    ae = get_ae(selected_term)

    st.divider()
    st.subheader(ae["term"])
    st.markdown(
        f'<div class="small-muted">{ae["soc"]} · MedDRA LLT Code: {ae["meddra_code"]}</div>',
        unsafe_allow_html=True
    )

    if ae["definition"] and ae["definition"] != "-":
        with st.expander("Definition"):
            st.write(ae["definition"])

    criteria = []
    for grade in range(1, 6):
        text = (ae.get(f"grade_{grade}") or "").strip()
        if text and text != "-":
            criteria.append({
                "grade": grade,
                "criterion": text,
                "label": f"Grade {grade} — {text}"
            })

    if not criteria:
        st.warning("No grade criterion is available for this term in the database.")
    else:
        selected_criterion = st.selectbox(
            "Patient value / clinical condition",
            options=criteria,
            index=None,
            format_func=lambda x: x["label"],
            placeholder="Select the matching CTCAE criterion…",
            help="Choose the criterion that best matches the patient's finding."
        )

        if selected_criterion:
            grade = selected_criterion["grade"]
            criterion = selected_criterion["criterion"]

            st.markdown(
                f"""
                <div class="result-card">
                    <div class="small-muted">CTCAE v6.0 RESULT</div>
                    <div class="grade-number">GRADE {grade}</div>
                    <div><strong>Selected criterion:</strong><br>{criterion}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with st.expander("Show all grading criteria"):
        for grade in range(1, 6):
            criterion = (ae.get(f"grade_{grade}") or "").strip()
            if criterion and criterion != "-":
                st.markdown(f"**Grade {grade}:** {criterion}")
            else:
                st.markdown(f"**Grade {grade}:** —")

    nav = (ae.get("navigational_note") or "").strip()
    if nav and nav != "-":
        st.info(f"Navigational note: {nav}")

st.divider()
st.caption(
    "Reference aid only. Verify grading against the protocol, investigator assessment, "
    "and the official NCI CTCAE v6.0 source before clinical-trial reporting."
)
