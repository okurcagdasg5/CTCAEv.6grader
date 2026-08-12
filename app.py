from pathlib import Path
import sqlite3
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "data" / "ctcae_v6.db"

st.set_page_config(
    page_title="CTCAE v6.0 Grader",
    page_icon="🧪",
    layout="centered"
)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@st.cache_data
def get_all_terms():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT term
            FROM ctcae
            ORDER BY term
            """
        ).fetchall()

    return [row["term"] for row in rows]


@st.cache_data
def get_term(term):
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
    "NCI Common Terminology Criteria for Adverse Events v6.0"
)


if not DB_PATH.exists():
    st.error("CTCAE database not found.")
    st.stop()


terms = get_all_terms()


selected_term = st.selectbox(
    "Adverse Event",
    options=terms,
    index=None,
    placeholder="AE seçin veya yazarak arayın..."
)


if selected_term:

    ae = get_term(selected_term)

    st.subheader(selected_term)

    definition = (ae.get("definition") or "").strip()

    if definition and definition != "-":
        st.info(definition)


    options = []

    for grade in range(1, 6):

        criterion = (
            ae.get(f"grade_{grade}") or ""
        ).strip()

        if criterion and criterion != "-":

            options.append(
                {
                    "grade": grade,
                    "criterion": criterion,
                    "label": f"Grade {grade} — {criterion}"
                }
            )


    selected = st.selectbox(
        "Patient value / clinical condition",
        options=options,
        index=None,
        format_func=lambda x: x["label"],
        placeholder="Uygun kriteri seçin..."
    )


    if selected:

        st.divider()

        st.metric(
            label="CTCAE Grade",
            value=f"Grade {selected['grade']}"
        )

        st.write("**Selected criterion:**")

        st.write(
            selected["criterion"]
        )


st.divider()

st.caption(
    "Reference aid only. Verify against the official NCI CTCAE v6.0 "
    "source and study protocol before clinical-trial reporting."
)
