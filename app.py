from __future__ import annotations

import html
import textwrap

import streamlit as st

from rag.service import TranscriptService


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Robotic Surgery Transcript Analyzer",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# GLOBAL CSS
# =========================================================

APP_CSS = """
<style>

@import url(
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
);

/* =======================================================
   GLOBAL
======================================================= */

html,
body,
[class*="css"] {
    font-family: "Inter", sans-serif;
}

.stApp {
    min-height: 100vh;

    background:
        radial-gradient(
            circle at 8% 5%,
            rgba(124, 92, 255, 0.16),
            transparent 24%
        ),
        radial-gradient(
            circle at 92% 8%,
            rgba(34, 211, 238, 0.09),
            transparent 22%
        ),
        radial-gradient(
            circle at 50% 100%,
            rgba(168, 85, 247, 0.07),
            transparent 26%
        ),
        #070b14;

    color: #f8fafc;
}

#MainMenu,
footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1450px;
    padding: 1.8rem 2.2rem 4rem;
}


/* =======================================================
   SIDEBAR
======================================================= */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #0a0f1b 0%,
            #080c15 100%
        );

    border-right:
        1px solid rgba(255, 255, 255, 0.07);
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.2rem;
}

.side-brand {
    padding:
        0.4rem
        0.2rem
        1.15rem;
}

.side-logo {
    width: 42px;
    height: 42px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 13px;

    background:
        linear-gradient(
            135deg,
            rgba(124, 92, 255, 0.28),
            rgba(34, 211, 238, 0.08)
        );

    border:
        1px solid rgba(124, 92, 255, 0.28);

    color: #ddd8ff;

    font-size: 1rem;
    font-weight: 800;

    box-shadow:
        0 8px 24px rgba(0, 0, 0, 0.25);
}

.side-title {
    margin-top: 0.65rem;

    color: #ffffff;

    font-size: 1rem;

    font-weight: 800;

    letter-spacing: -0.02em;
}

.side-subtitle {
    margin-top: 0.16rem;

    color: #7f8ba0;

    font-size: 0.7rem;

    line-height: 1.55;
}


/* =======================================================
   HERO
======================================================= */

.hero {
    position: relative;

    overflow: hidden;

    padding:
        2.45rem
        2.65rem;

    margin-bottom: 1.25rem;

    border-radius: 27px;

    border:
        1px solid rgba(255, 255, 255, 0.08);

    background:
        linear-gradient(
            135deg,
            rgba(124, 92, 255, 0.16),
            rgba(34, 211, 238, 0.035)
        ),
        rgba(9, 15, 27, 0.78);

    box-shadow:
        0 25px 70px rgba(0, 0, 0, 0.28);

    backdrop-filter: blur(18px);

    animation:
        fadeUp 0.65s ease-out;
}

.hero::after {
    content: "";

    position: absolute;

    width: 400px;
    height: 400px;

    right: -130px;
    top: -250px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(124, 92, 255, 0.24),
            transparent 68%
        );

    animation:
        heroGlow 7s ease-in-out infinite;
}

.hero-badge {
    position: relative;
    z-index: 2;

    display: inline-flex;

    align-items: center;

    padding:
        6px
        11px;

    border-radius: 999px;

    background:
        rgba(124, 92, 255, 0.09);

    border:
        1px solid rgba(124, 92, 255, 0.25);

    color: #d0caff;

    font-size: 0.67rem;

    font-weight: 800;

    letter-spacing: 0.11em;

    text-transform: uppercase;
}

.hero-title {
    position: relative;
    z-index: 2;

    margin-top: 0.95rem;

    font-size: 2.5rem;

    line-height: 1.07;

    font-weight: 800;

    letter-spacing: -0.045em;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #d8d2ff 48%,
            #b8fff2
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    position: relative;
    z-index: 2;

    max-width: 860px;

    margin-top: 0.85rem;

    color: #99a5b8;

    font-size: 0.95rem;

    line-height: 1.75;
}


/* =======================================================
   KPI CARDS
======================================================= */

.kpi-grid {
    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 13px;

    margin:
        1rem
        0
        1.5rem;
}

.kpi-card {
    padding:
        1.05rem
        1.15rem;

    border-radius: 18px;

    border:
        1px solid rgba(255, 255, 255, 0.07);

    background:
        linear-gradient(
            145deg,
            rgba(255, 255, 255, 0.055),
            rgba(255, 255, 255, 0.015)
        );

    transition:
        transform 0.22s ease,
        border-color 0.22s ease,
        box-shadow 0.22s ease;

    animation:
        fadeUp 0.5s ease-out;
}

.kpi-card:hover {
    transform:
        translateY(-4px);

    border-color:
        rgba(124, 92, 255, 0.35);

    box-shadow:
        0
        16px
        36px
        rgba(0, 0, 0, 0.25);
}

.kpi-label {
    color: #8591a5;

    font-size: 0.66rem;

    font-weight: 700;

    letter-spacing: 0.1em;

    text-transform: uppercase;
}

.kpi-value {
    margin-top: 0.35rem;

    color: #ffffff;

    font-size: 1.5rem;

    font-weight: 800;
}


/* =======================================================
   SECTION TYPOGRAPHY
======================================================= */

.kicker {
    color: #9d94ff;

    font-size: 0.67rem;

    font-weight: 800;

    letter-spacing: 0.13em;

    text-transform: uppercase;
}

.section-title {
    margin-top: 0.25rem;

    color: #f8fafc;

    font-size: 1.4rem;

    font-weight: 800;

    letter-spacing: -0.025em;
}

.question-chip {
    display: inline-block;

    padding:
        5px
        10px;

    border-radius: 999px;

    background:
        rgba(34, 211, 238, 0.07);

    border:
        1px solid rgba(34, 211, 238, 0.14);

    color: #91eee5;

    font-size: 0.66rem;

    font-weight: 800;

    letter-spacing: 0.08em;
}


/* =======================================================
   ANSWER CARD
======================================================= */

.answer-card {
    margin:
        1rem
        0
        1.15rem;

    padding:
        1.3rem
        1.4rem;

    border-radius: 20px;

    border:
        1px solid rgba(124, 92, 255, 0.18);

    border-left:
        4px solid #8b7cff;

    background:
        linear-gradient(
            135deg,
            rgba(124, 92, 255, 0.10),
            rgba(34, 211, 238, 0.025)
        );

    animation:
        fadeUp 0.4s ease-out;
}

.answer-label {
    color: #aaa2ff;

    font-size: 0.66rem;

    font-weight: 800;

    letter-spacing: 0.1em;

    text-transform: uppercase;
}

.answer-text {
    margin-top: 0.55rem;

    color: #eef2ff;

    font-size: 0.96rem;

    line-height: 1.8;
}


/* =======================================================
   SOURCE CARDS
======================================================= */

.source-card {
    margin:
        0.65rem
        0;

    padding:
        1rem
        1.1rem;

    border-radius: 16px;

    border:
        1px solid rgba(255, 255, 255, 0.065);

    background:
        rgba(11, 17, 29, 0.76);

    transition:
        transform 0.2s ease,
        border-color 0.2s ease,
        background 0.2s ease;

    animation:
        fadeUp 0.35s ease-out;
}

.source-card:hover {
    transform:
        translateX(4px);

    border-color:
        rgba(34, 211, 238, 0.21);

    background:
        rgba(17, 25, 41, 0.92);
}

.source-line {
    display: flex;

    align-items: center;

    gap: 8px;

    flex-wrap: wrap;
}

.source-market {
    color: #ffffff;

    font-size: 0.82rem;

    font-weight: 750;
}

.source-time {
    padding:
        3px
        8px;

    border-radius: 999px;

    background:
        rgba(34, 211, 238, 0.07);

    border:
        1px solid rgba(34, 211, 238, 0.15);

    color: #91eee5;

    font-size: 0.64rem;

    font-weight: 800;
}

.source-meta {
    margin-top: 0.35rem;

    color: #7f8ba0;

    font-size: 0.69rem;
}

.source-quote {
    margin-top: 0.58rem;

    color: #dfe6f3;

    font-size: 0.88rem;

    line-height: 1.7;
}


/* =======================================================
   INFO / STATUS
======================================================= */

.status-card {
    padding:
        0.95rem
        1rem;

    border-radius: 15px;

    border:
        1px solid rgba(255, 255, 255, 0.06);

    background:
        rgba(255, 255, 255, 0.025);

    color: #97a3b7;

    font-size: 0.76rem;

    line-height: 1.65;
}

.status-card strong {
    color: #ffffff;
}


/* =======================================================
   BUTTONS
======================================================= */

.stButton > button {
    min-height: 42px;

    border-radius:
        12px
        !important;

    border:
        1px solid rgba(124, 92, 255, 0.23)
        !important;

    background:
        linear-gradient(
            135deg,
            rgba(124, 92, 255, 0.17),
            rgba(34, 211, 238, 0.04)
        )
        !important;

    color:
        #ffffff
        !important;

    font-weight:
        700
        !important;

    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        border-color 0.18s ease
        !important;
}

.stButton > button:hover {
    transform:
        translateY(-2px);

    border-color:
        rgba(124, 92, 255, 0.46)
        !important;

    box-shadow:
        0
        10px
        25px
        rgba(0, 0, 0, 0.24);
}


/* =======================================================
   SELECTBOX / FILE UPLOADER
======================================================= */

div[data-baseweb="select"] > div {
    background:
        rgba(15, 21, 35, 0.92)
        !important;

    border:
        1px solid rgba(255, 255, 255, 0.07)
        !important;

    border-radius:
        12px
        !important;
}

div[data-baseweb="select"] > div:hover {
    border-color:
        rgba(124, 92, 255, 0.32)
        !important;
}

div[data-testid="stFileUploaderDropzone"] {
    border-radius: 14px;

    border:
        1px dashed rgba(124, 92, 255, 0.25);

    background:
        rgba(255, 255, 255, 0.018);
}


/* =======================================================
   TABS
======================================================= */

button[data-baseweb="tab"] {
    padding:
        0.55rem
        0.95rem;

    border-radius: 11px;

    color:
        #8993a7
        !important;

    font-weight:
        750
        !important;

    transition:
        background 0.18s ease,
        color 0.18s ease;
}

button[data-baseweb="tab"]:hover {
    color:
        #ffffff
        !important;

    background:
        rgba(255, 255, 255, 0.035);
}

button[data-baseweb="tab"][aria-selected="true"] {
    color:
        #ffffff
        !important;

    background:
        linear-gradient(
            135deg,
            rgba(124, 92, 255, 0.15),
            rgba(34, 211, 238, 0.035)
        );
}


/* =======================================================
   EXPANDERS
======================================================= */

details {
    border-radius:
        16px
        !important;

    border:
        1px solid rgba(255, 255, 255, 0.06)
        !important;

    background:
        rgba(14, 20, 34, 0.65)
        !important;
}


/* =======================================================
   CHAT
======================================================= */

[data-testid="stChatMessage"] {
    border-radius: 17px;

    border:
        1px solid rgba(255, 255, 255, 0.05);

    animation:
        fadeUp 0.3s ease-out;
}


/* =======================================================
   ANIMATIONS
======================================================= */

@keyframes fadeUp {

    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }

}

@keyframes heroGlow {

    0%, 100% {
        transform:
            translate(0, 0)
            scale(1);

        opacity: 0.65;
    }

    50% {
        transform:
            translate(-18px, 16px)
            scale(1.08);

        opacity: 1;
    }

}

@media (max-width: 850px) {

    .block-container {
        padding:
            1rem
            1rem
            3rem;
    }

    .hero {
        padding: 1.7rem;
    }

    .hero-title {
        font-size: 1.85rem;
    }

    .kpi-grid {
        grid-template-columns: 1fr;
    }

}

</style>
"""


st.markdown(
    APP_CSS,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

if "service" not in st.session_state:
    st.session_state.service = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# =========================================================
# HELPERS
# =========================================================

def render_html(content: str) -> None:
    """Render raw HTML using Streamlit's native HTML renderer."""
    st.html(
        textwrap.dedent(content).strip()
    )


def esc(value: object) -> str:
    """Escape text before inserting it into HTML."""
    return html.escape(str(value))


def load_uploaded_transcripts(uploaded_files) -> None:
    """Load exactly three uploaded transcript files."""

    if len(uploaded_files) != 3:
        st.error(
            "Please upload exactly 3 transcript files."
        )
        return

    try:
        with st.spinner(
            "Parsing transcripts and building retrieval index..."
        ):
            service = (
                TranscriptService.from_uploaded_files(
                    uploaded_files
                )
            )

        st.session_state.service = service
        st.session_state.chat_history = []

        st.success(
            "Three transcripts loaded successfully."
        )

    except Exception as exc:
        st.error(
            f"Could not process the transcripts: {exc}"
        )


def load_demo_transcripts() -> None:
    """Load the provided sample transcripts."""

    try:
        with st.spinner(
            "Loading provided transcripts..."
        ):
            service = TranscriptService.from_folder(
                "data"
            )

        st.session_state.service = service
        st.session_state.chat_history = []

        st.success(
            "Sample transcripts loaded successfully."
        )

    except Exception as exc:
        st.error(
            f"Could not load sample transcripts: {exc}"
        )


def render_source(source: dict) -> None:
    """Render an exact transcript source."""

    render_html(
        f"""
        <div class="source-card">

            <div class="source-line">

                <span class="source-market">
                    {esc(source.get("market", "Unknown market"))}
                </span>

                <span class="source-time">
                    {esc(source.get("timestamp", "—"))}
                </span>

            </div>

            <div class="source-meta">
                {esc(source.get("expert", "Unknown expert"))}
                ·
                {esc(source.get("speaker", "Unknown speaker"))}
                {(
                    " · "
                    + esc(source.get("source_file", ""))
                    if source.get("source_file")
                    else ""
                )}
            </div>

            <div class="source-quote">
                “{esc(source.get("quote", ""))}”
            </div>

        </div>
        """
    )


def render_sources(
    sources: list[dict],
) -> None:
    """Render a collection of transcript sources."""

    if not sources:
        st.info(
            "No supporting transcript evidence found."
        )
        return

    for source in sources:
        render_source(source)


def render_kpis(
    service: TranscriptService,
) -> None:
    """Render summary KPI cards."""

    experts = service.get_experts()

    markets = sorted(
        {
            expert["market"]
            for expert in experts
        }
    )

    render_html(
        f"""
        <div class="kpi-grid">

            <div class="kpi-card">

                <div class="kpi-label">
                    Experts analyzed
                </div>

                <div class="kpi-value">
                    {len(experts)}
                </div>

            </div>

            <div class="kpi-card">

                <div class="kpi-label">
                    Expert responses
                </div>

                <div class="kpi-value">
                    {len(service.chunks)}
                </div>

            </div>

            <div class="kpi-card">

                <div class="kpi-label">
                    Markets covered
                </div>

                <div class="kpi-value">
                    {len(markets)}
                </div>

            </div>

        </div>
        """
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    render_html(
        """
        <div class="side-brand">

            <div class="side-logo">
                ◈
            </div>

            <div class="side-title">
                Transcript Intelligence
            </div>

            <div class="side-subtitle">
                Evidence-first expert interview analysis
            </div>

        </div>
        """
    )

    st.markdown(
        "### Load transcripts"
    )

    uploaded_files = st.file_uploader(
        "Upload 3 expert transcripts",
        type=["txt"],
        accept_multiple_files=True,
        help="Upload exactly three TXT transcript files.",
    )

    if st.button(
        "Analyze Uploads",
        use_container_width=True,
        disabled=not uploaded_files,
    ):
        load_uploaded_transcripts(
            uploaded_files
        )

    st.markdown("---")

    st.markdown(
        "### Demo"
    )

    if st.button(
        "Load Sample Transcripts",
        use_container_width=True,
    ):
        load_demo_transcripts()

    if st.session_state.service is not None:

        st.markdown("---")

        render_html(
            """
            <div class="status-card">

                <strong>
                    ● Analysis ready
                </strong>

                <br>

                Quotes are linked directly to
                expert, market, timestamp and
                source transcript.

            </div>
            """
        )

        st.write("")

        if st.button(
            "Clear Analysis",
            use_container_width=True,
        ):
            st.session_state.service = None
            st.session_state.chat_history = []
            st.rerun()


# =========================================================
# HERO
# =========================================================

render_html(
    """
    <div class="hero">

        <div class="hero-badge">
            ✦ AI Research Workspace
        </div>

        <div class="hero-title">
            European Robotic Surgery
            <br>
            Transcript Analyzer
        </div>

        <div class="hero-subtitle">
            Analyze expert interviews across France,
            Germany and the United Kingdom using
            source-grounded answers, exact quotes,
            timestamps, cross-market comparisons
            and transcript-based Q&A.
        </div>

    </div>
    """
)


# =========================================================
# EMPTY STATE
# =========================================================

if st.session_state.service is None:

    render_html(
        """
        <div class="kicker">
            Get started
        </div>

        <div class="section-title">
            Load your interview evidence
        </div>
        """
    )

    left, right = st.columns(2)

    with left:
        render_html(
            """
            <div class="status-card">

                <strong>
                    Upload mode
                </strong>

                <br><br>

                Upload the three TXT transcripts
                from the assignment. Speaker labels
                and timestamps are parsed automatically.

            </div>
            """
        )

    with right:
        render_html(
            """
            <div class="status-card">

                <strong>
                    Demo mode
                </strong>

                <br><br>

                Load the provided sample transcripts
                directly from the project's
                <code>data/</code> folder.

            </div>
            """
        )

    st.stop()


# =========================================================
# ACTIVE SERVICE
# =========================================================

service: TranscriptService = (
    st.session_state.service
)

render_kpis(service)


# =========================================================
# TABS
# =========================================================

guide_tab, comparison_tab, chat_tab = st.tabs(
    [
        "📋 Interview Guide",
        "◌ Comparison",
        "✦ Ask AI",
    ]
)


# =========================================================
# INTERVIEW GUIDE
# =========================================================

with guide_tab:

    render_html(
        """
        <div class="kicker">
            Structured analysis
        </div>

        <div class="section-title">
            Interview Guide
        </div>
        """
    )

    questions = service.get_guide_questions()
    experts = service.get_experts()

    question_map = {
        f"{question.question_id} — "
        f"{question.topic}": question
        for question in questions
    }

    selected_question_label = st.selectbox(
        "Select interview-guide question",
        list(question_map.keys()),
        label_visibility="collapsed",
    )

    selected_question = question_map[
        selected_question_label
    ]

    render_html(
        f"""
        <div style="margin-top:1rem">

            <span class="question-chip">
                {esc(selected_question.question_id)}
            </span>

            <div class="section-title"
                 style="margin-top:.65rem">

                {esc(selected_question.question)}

            </div>

        </div>
        """
    )

    market_options = [
        expert["market"]
        for expert in experts
    ]

    selected_market = st.selectbox(
        "Select expert / market",
        market_options,
        label_visibility="collapsed",
    )

    result = service.get_guide_answer(
        question_id=selected_question.question_id,
        market=selected_market,
    )

    render_html(
        f"""
        <div class="kpi-grid"
             style="margin-top:1rem">

            <div class="kpi-card">

                <div class="kpi-label">
                    Market
                </div>

                <div class="kpi-value"
                     style="font-size:1.08rem">

                    {esc(result["market"])}

                </div>

            </div>

            <div class="kpi-card">

                <div class="kpi-label">
                    Expert
                </div>

                <div class="kpi-value"
                     style="font-size:1.08rem">

                    {esc(result["expert"])}

                </div>

            </div>

            <div class="kpi-card">

                <div class="kpi-label">
                    Role
                </div>

                <div class="kpi-value"
                     style="font-size:1.08rem">

                    {esc(result["role"])}

                </div>

            </div>

        </div>
        """
    )

    render_html(
        f"""
        <div class="answer-card">

            <div class="answer-label">
                Grounded answer
            </div>

            <div class="answer-text">
                {esc(result["answer"])}
            </div>

        </div>
        """
    )

    render_html(
        """
        <div class="kicker">
            Traceable evidence
        </div>

        <div class="section-title"
             style="font-size:1.05rem">

            Exact transcript sources

        </div>
        """
    )

    render_sources(
        result["sources"]
    )


# =========================================================
# COMPARISON
# =========================================================

with comparison_tab:

    render_html(
        """
        <div class="kicker">
            Cross-market analysis
        </div>

        <div class="section-title">
            Common Themes & Documented Differences
        </div>
        """
    )

    comparison = service.get_comparison()

    st.markdown(
        "#### Common themes"
    )

    themes = comparison["common_themes"]

    if not themes:
        st.info(
            "No common themes were detected."
        )

    for theme in themes:

        with st.expander(
            f"◈ {theme['theme']}",
            expanded=True,
        ):

            st.caption(
                "Observed across: "
                + ", ".join(theme["markets"])
            )

            shown_markets: set[str] = set()

            for evidence in theme["evidence"]:

                market = evidence["market"]

                if market in shown_markets:
                    continue

                shown_markets.add(market)

                render_source(
                    {
                        "market": evidence["market"],
                        "expert": evidence["expert"],
                        "timestamp": evidence["timestamp"],
                        "speaker": evidence["expert"],
                        "quote": evidence["quote"],
                    }
                )

    st.markdown("---")

    st.markdown(
        "#### Documented differences"
    )

    for difference in comparison["differences"]:

        with st.expander(
            difference["topic"],
            expanded=True,
        ):

            render_html(
                f"""
                <div class="answer-card">

                    <div class="answer-label">
                        Comparison
                    </div>

                    <div class="answer-text">
                        {esc(
                            difference["interpretation"]
                        )}
                    </div>

                </div>
                """
            )

            for evidence in difference["evidence"]:

                render_source(
                    {
                        "market": evidence["market"],
                        "expert": evidence["expert"],
                        "timestamp": evidence["timestamp"],
                        "speaker": evidence["expert"],
                        "quote": evidence["quote"],
                    }
                )


# =========================================================
# ASK AI
# =========================================================

with chat_tab:

    render_html(
        """
        <div class="kicker">
            Cross-transcript Q&A
        </div>

        <div class="section-title">
            Ask AI
        </div>
        """
    )

    render_html(
        """
        <div class="status-card"
             style="margin:.8rem 0 1.1rem">

            Ask a question across all loaded transcripts.
            Answers use retrieved transcript evidence and
            include the supporting quote and timestamp.

        </div>
        """
    )

    for message in st.session_state.chat_history:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )

            if (
                message["role"] == "assistant"
                and message.get("sources")
            ):

                st.markdown(
                    "#### Evidence"
                )

                render_sources(
                    message["sources"]
                )

    user_question = st.chat_input(
        "Ask across all three transcripts..."
    )

    if user_question:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_question,
            }
        )

        with st.chat_message("user"):
            st.write(
                user_question
            )

        with st.chat_message("assistant"):

            with st.spinner(
                "Searching transcript evidence..."
            ):

                try:

                    result = service.ask(
                        question=user_question,
                        top_k=6,
                    )

                    answer = result["answer"]
                    sources = result["sources"]

                    render_html(
                        f"""
                        <div class="answer-card">

                            <div class="answer-label">
                                Transcript-grounded response
                            </div>

                            <div class="answer-text">
                                {esc(answer)}
                            </div>

                        </div>
                        """
                    )

                    if sources:

                        st.markdown(
                            "#### Evidence"
                        )

                        render_sources(
                            sources
                        )

                    else:

                        st.info(
                            "No supporting evidence found."
                        )

                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                        }
                    )

                except Exception as exc:

                    error_message = (
                        "Could not answer the question: "
                        f"{exc}"
                    )

                    st.error(
                        error_message
                    )

                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": error_message,
                            "sources": [],
                        }
                    )