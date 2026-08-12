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
.block-container {
    max-width: 1000px;
    padding-top: 2rem;
}

.grade-card {
    border: 1px solid rgba(128,128,128,.28);
    border-radius: 14px;
    padding: 16px 18px;
    margin: 10px 0;
}

.grade-title {
    font-size: 1.15rem;
    font-weight: 800;
    margin-bottom: 8px;
}

.result-card {
    border: 2px solid rgba(128,128,128,.35);
    border-radius: 16px;
    padding: 22px;
    margin-top: 16px;
}

.result-grade {
    font-size: 2.2rem;
    font-weight: 900;
}

.small-muted {
    opacity: .72;
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
                """
                SELECT term
                FROM ctcae
                WHERE soc = ?
                ORDER BY term
                """,
                (soc,)
            ).fetchall()

        else:
            rows = conn.execute(
                """
                SELECT term
                FROM ctcae
                ORDER BY term
                """
            ).fetchall()

    return [r["term"] for r in rows]


@st.cache_data
def get_ae(term):
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM ctcae
            WHERE term = ?
            """,
            (term,)
        ).fetchone()

    return dict(row) if row else None


st.title("CTCAE v6.0 Grader")

st.caption(
    "NCI Common Terminology Criteria for Adverse Events "
    "— v6.0 / MedDRA 28.0"
)

if not DB_PATH.exists():
    st.error("CTCAE database was not found.")
    st.stop()


selected_soc = st.selectbox(
    "Category (SOC)",
    ["All categories"] + load_socs(),
    help="Optional: filter adverse events by System Organ Class."
)


selected_term = st.selectbox(
    "Adverse Event",
    options=load_terms(selected_soc),
    index=None,
    placeholder="Type to search for an adverse event…"
)


if selected_term:

    ae = get_ae(selected_term)

    st.divider()

    st.subheader(ae["term"])

    st.markdown(
        f"""
        <div class="small-muted">
        {ae["soc"]} · MedDRA LLT Code: {ae["meddra_code"]}
        </div>
        """,
        unsafe_allow_html=True
    )


    definition = (ae.get("definition") or "").strip()

    if definition and definition != "-":

        st.markdown("### Definition")

        st.write(definition)


    criteria = []

    for grade in range(1, 6):

        criterion = (
            ae.get(f"grade_{grade}") or ""
        ).strip()

        if criterion and criterion != "-":

            criteria.append(
                {
                    "grade": grade,
                    "criterion": criterion,
                    "label": f"Grade {grade} — {criterion}"
                }
            )


    st.markdown("### Official CTCAE v6.0 Grade Criteria")


    if not criteria:

        st.warning(
            "No grade criteria are available for this CTCAE term."
        )

    else:

        for item in criteria:

            st.markdown(
                f"""
                <div class="grade-card">

                    <div class="grade-title">
                        GRADE {item["grade"]}
                    </div>

                    <div>
                        {item["criterion"]}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


        st.markdown("### Grade the Patient")


        selected_criterion = st.selectbox(

            "Patient value / clinical condition",

            options=criteria,

            index=None,

            format_func=lambda x: x["label"],

            placeholder="Select the matching CTCAE criterion…",

            help=(
                "Select the CTCAE criterion that best "
                "matches the patient's finding."
            )
        )


        if selected_criterion:

            grade = selected_criterion["grade"]

            criterion = selected_criterion["criterion"]


            st.markdown(
                f"""
                <div class="result-card">

                    <div class="small-muted">
                        CTCAE v6.0 RESULT
                    </div>

                    <div class="result-grade">
                        GRADE {grade}
                    </div>

                    <br>

                    <strong>Selected criterion</strong>

                    <br>

                    {criterion}

                </div>
                """,
                unsafe_allow_html=True
            )


    nav = (
        ae.get("navigational_note") or ""
    ).strip()


    if nav and nav != "-":

        st.markdown("### Navigational Note")

        st.info(nav)


st.divider()

st.caption(
    "Reference aid only. Verify grading against the study protocol, "
    "investigator assessment, sponsor instructions, and the official "
    "NCI CTCAE v6.0 source."
)
