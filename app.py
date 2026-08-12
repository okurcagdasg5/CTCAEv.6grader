from pathlib import Path
import sqlite3
import streamlit as st


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "data" / "ctcae_v6.db"


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="CTCAE v6.0 Grader",
    page_icon="🧪",
    layout="centered",
)


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@st.cache_data
def load_socs():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT soc
            FROM ctcae
            WHERE soc IS NOT NULL
              AND TRIM(soc) != ''
            ORDER BY soc
            """
        ).fetchall()

    return [row["soc"] for row in rows]


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

    return [row["term"] for row in rows]


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


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("CTCAE v6.0 Grader")

st.caption(
    "NCI Common Terminology Criteria for Adverse Events "
    "— CTCAE v6.0 / MedDRA 28.0"
)


# ---------------------------------------------------------
# DATABASE CHECK
# ---------------------------------------------------------

if not DB_PATH.exists():
    st.error(
        "CTCAE database could not be found. "
        "Expected file: data/ctcae_v6.db"
    )
    st.stop()


# ---------------------------------------------------------
# FILTERS
# ---------------------------------------------------------

soc_options = ["All categories"] + load_socs()

selected_soc = st.selectbox(
    "Category (SOC)",
    options=soc_options,
    help="Optionally filter adverse events by System Organ Class."
)


terms = load_terms(selected_soc)

selected_term = st.selectbox(
    "Adverse Event",
    options=terms,
    index=None,
    placeholder="Type to search for an adverse event..."
)


# ---------------------------------------------------------
# AE DETAILS
# ---------------------------------------------------------

if selected_term:

    ae = get_ae(selected_term)

    if ae is None:
        st.error("The selected adverse event could not be loaded.")
        st.stop()

    st.divider()

    st.header(ae["term"])

    soc = (ae.get("soc") or "").strip()
    meddra_code = (ae.get("meddra_code") or "").strip()

    meta_parts = []

    if soc:
        meta_parts.append(soc)

    if meddra_code:
        meta_parts.append(f"MedDRA LLT Code: {meddra_code}")

    if meta_parts:
        st.caption(" • ".join(meta_parts))


    # -----------------------------------------------------
    # DEFINITION
    # -----------------------------------------------------

    definition = (ae.get("definition") or "").strip()

    if definition and definition != "-":
        st.subheader("Definition")
        st.write(definition)


    # -----------------------------------------------------
    # BUILD GRADE CRITERIA
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # DISPLAY OFFICIAL CRITERIA
    # -----------------------------------------------------

    st.subheader("Official CTCAE v6.0 Grade Criteria")

    if not criteria:

        st.warning(
            "No grading criteria are available for this adverse event."
        )

    else:

        for item in criteria:

            with st.container(border=True):

                st.markdown(
                    f"### GRADE {item['grade']}"
                )

                st.write(
                    item["criterion"]
                )


        # -------------------------------------------------
        # GRADING SELECTION
        # -------------------------------------------------

        st.subheader("Grade the Patient")

        selected_criterion = st.selectbox(
            "Patient value / clinical condition",
            options=criteria,
            index=None,
            format_func=lambda item: item["label"],
            placeholder="Select the matching CTCAE criterion...",
            help=(
                "Select the official CTCAE criterion that best "
                "matches the patient's finding."
            )
        )


        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        if selected_criterion:

            grade = selected_criterion["grade"]
            criterion = selected_criterion["criterion"]

            st.divider()

            with st.container(border=True):

                st.caption("CTCAE v6.0 RESULT")

                st.markdown(
                    f"# GRADE {grade}"
                )

                st.markdown(
                    "**Selected criterion**"
                )

                st.write(
                    criterion
                )


    # -----------------------------------------------------
    # NAVIGATIONAL NOTE
    # -----------------------------------------------------

    navigational_note = (
        ae.get("navigational_note") or ""
    ).strip()

    if navigational_note and navigational_note != "-":

        st.subheader("Navigational Note")

        st.info(
            navigational_note
        )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "Reference aid only. Verify grading against the official "
    "NCI CTCAE v6.0 source, study protocol, sponsor instructions, "
    "and investigator assessment before clinical-trial reporting."
)
