
import json
import os
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path

import requests
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FEEDBACK_FILE = DATA_DIR / "feedback.jsonl"

API_URL = os.getenv("JALSANCHAY_API_URL", "http://127.0.0.1:8000")

ROOF_COEFFICIENTS = {
    "GI sheet": 0.90,
    "Asbestos": 0.80,
    "Tiled roof": 0.75,
    "Concrete roof": 0.70,
}

st.set_page_config(
    page_title="JalSanchay | Water Management",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)



st.markdown("""
<style>
/* ===== Global application theme ===== */
.stApp {
    background-color: #F4F7FB;
    color: #172B4D;
}

section[data-testid="stMain"] {
    background-color: #F4F7FB;
}

/* ===== Headings and text ===== */
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp p,
.stApp label,
.stApp [data-testid="stMarkdownContainer"] {
    color: #172B4D;
}

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background-color: #E8EEF6;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #172B4D;
}

/* ===== Text and number inputs ===== */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background-color: #FFFFFF !important;
    color: #172B4D !important;
    -webkit-text-fill-color: #172B4D !important;
    border: 1px solid #94A3B8 !important;
    border-radius: 7px !important;
}

/* ===== Input placeholders ===== */
.stTextInput input::placeholder,
.stNumberInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #64748B !important;
    -webkit-text-fill-color: #64748B !important;
    opacity: 1 !important;
}

/* ===== Dropdowns and select boxes ===== */
[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #172B4D !important;
    border-color: #94A3B8 !important;
}

[data-baseweb="select"] input,
[data-baseweb="select"] span {
    color: #172B4D !important;
}

/* Dropdown menu options */
[data-baseweb="menu"],
[role="listbox"],
[role="option"] {
    background-color: #FFFFFF !important;
    color: #172B4D !important;
}

[role="option"]:hover {
    background-color: #E2EAF4 !important;
}

/* ===== Buttons ===== */
.stButton button,
.stDownloadButton button,
button[kind="primary"] {
    background-color: #0F766E !important;
    color: #FFFFFF !important;
    border: 1px solid #0F766E !important;
    border-radius: 8px !important;
}

.stButton button p,
.stDownloadButton button p {
    color: #FFFFFF !important;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background-color: #115E59 !important;
    border-color: #115E59 !important;
}

/* ===== Chat messages ===== */
[data-testid="stChatMessage"] {
    background-color: #FFFFFF !important;
    color: #172B4D !important;
    border: 1px solid #D5DEE9 !important;
    border-radius: 10px;
    padding: 12px;
}

/* ===== Chat input ===== */
[data-testid="stChatInput"] textarea {
    background-color: #FFFFFF !important;
    color: #172B4D !important;
    -webkit-text-fill-color: #172B4D !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #64748B !important;
}

/* ===== Tabs ===== */
button[data-baseweb="tab"] {
    color: #334155 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #0F766E !important;
}

/* ===== Radio buttons and checkboxes ===== */
[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label {
    color: #172B4D !important;
}

/* ===== Expanders ===== */
[data-testid="stExpander"] {
    background-color: #FFFFFF;
    border: 1px solid #D5DEE9;
    border-radius: 8px;
}

/* ===== Markdown content ===== */
.stMarkdown,
.stMarkdown p,
.stMarkdown li {
    color: #172B4D;
}

/* ===== Links ===== */
.stApp a {
    color: #0F766E !important;
}

/* ===== Horizontal separators ===== */
hr {
    border-color: #D5DEE9 !important;
}

/* ===== Streamlit status messages ===== */

/* Error messages */
[data-testid="stAlert"][data-alert-type="error"] {
    background-color: #FEE2E2 !important;
    border: 1px solid #DC2626 !important;
}

[data-testid="stAlert"][data-alert-type="error"] p,
[data-testid="stAlert"][data-alert-type="error"] span,
[data-testid="stAlert"][data-alert-type="error"] div {
    color: #991B1B !important;
}

/* Warning messages */
[data-testid="stAlert"][data-alert-type="warning"] {
    background-color: #FEF3C7 !important;
    border: 1px solid #D97706 !important;
}

/* Success messages */
[data-testid="stAlert"][data-alert-type="success"] {
    background-color: #DCFCE7 !important;
    border: 1px solid #16A34A !important;
}

/* Information messages */
[data-testid="stAlert"][data-alert-type="info"] {
    background-color: #DBEAFE !important;
    border: 1px solid #2563EB !important;
}

/* ===== General text contrast ===== */
.stApp input,
.stApp textarea,
.stApp select {
    color: #172B4D !important;
}

.stApp [data-testid="stWidgetLabel"] p {
    color: #172B4D !important;
}

/* Disabled and placeholder text */
.stApp input:disabled,
.stApp textarea:disabled {
    color: #475569 !important;
    -webkit-text-fill-color: #475569 !important;
}

</style>
""", unsafe_allow_html=True)





def initialize_state():
    defaults = {
        "chat_history": [],
        "thread_id": str(uuid.uuid4()),
        "pending_approval": False,
        "pending_thread_id": None,
        "pending_inputs": None,
        "calculation_result": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_state()




def save_feedback(question, answer, rating):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    feedback = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer,
        "rating": rating,
    }

    with FEEDBACK_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(feedback, ensure_ascii=False) + "\n")


def extract_answer(data):
    """Extract answer and citations from API responses."""

    if not isinstance(data, dict):
        return str(data), []

    result = data.get("result", data)

    if isinstance(result, dict) and "result" in result:
        result = result["result"]

    if not isinstance(result, dict):
        return str(result), []

    answer = result.get(
        "answer",
        result.get("message", str(result))
    )

    citations = result.get("citations", [])

    return answer, citations


def display_citations(citations):
    if not citations:
        return

    st.markdown("**Sources and references**")

    for citation in citations:
        document = citation.get("document", "Source document")
        page = citation.get("page", "Not specified")
        source_url = citation.get("source_url")

        st.markdown(
            f"""
            <div class="source-card">
                <div class="source-title">{document}</div>
                <div class="source-detail">Page {page}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if source_url:
            st.markdown(f"[Open source document]({source_url})")


def display_metric(label, value):
    st.markdown(
        f"""
        <div class="info-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )




def generate_design_sheet(
    roof_area,
    rainfall,
    roof_type,
    persons,
    daily_demand,
    dry_days,
):
    coefficient = ROOF_COEFFICIENTS[roof_type]

    annual_collection = rainfall * roof_area * coefficient
    household_demand = persons * daily_demand * dry_days

    difference = annual_collection - household_demand
    coverage = (annual_collection / household_demand) * 100

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=19 * mm,
        leftMargin=19 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#123B4A"),
        alignment=TA_CENTER,
        spaceAfter=5,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#718096"),
        alignment=TA_CENTER,
        spaceAfter=15,
    )

    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#087E8B"),
        spaceBefore=12,
        spaceAfter=7,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=5,
    )

    story = [
        Paragraph("JalSanchay", title_style),
        Paragraph(
            "ROOFTOP RAINWATER HARVESTING DESIGN SHEET",
            subtitle_style,
        ),
    ]

    story.append(
        Paragraph("1. Site and household information", section_style)
    )

    input_data = [
        ["Parameter", "Design value"],
        ["Roof area", f"{roof_area:.2f} m²"],
        ["Annual rainfall", f"{rainfall:.2f} mm"],
        ["Roof type", roof_type],
        ["Runoff coefficient", str(coefficient)],
        ["Household members", str(persons)],
        ["Daily demand per person", f"{daily_demand:.2f} litres"],
        ["Dry period", f"{dry_days} days"],
    ]

    table = Table(input_data, colWidths=[78 * mm, 88 * mm])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#087E8B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DCE5EB")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F3F8FA")]),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))

    story.append(table)

    story.append(
        Paragraph("2. Rainwater potential and demand", section_style)
    )

    calculation_data = [
        ["Calculation", "Result"],
        ["Annual rainwater collection", f"{annual_collection:,.2f} litres"],
        ["Household demand", f"{household_demand:,.2f} litres"],
        ["Surplus / deficit", f"{difference:,.2f} litres"],
        ["Demand coverage", f"{coverage:.2f}%"],
    ]

    table = Table(calculation_data, colWidths=[78 * mm, 88 * mm])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#087E8B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DCE5EB")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F3F8FA")]),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))

    story.append(table)

    story.append(
        Paragraph("3. Preliminary system recommendations", section_style)
    )

    story.append(Paragraph(
        f"<b>Storage tank:</b> A preliminary usable storage capacity "
        f"of {household_demand:,.0f} litres would cover the specified "
        f"{dry_days}-day household demand if the tank starts full. "
        "Actual tank sizing should account for rainfall timing, "
        "available space, collection losses and supply reliability.",
        body_style,
    ))

    story.append(Paragraph(
        "<b>Recharge pit:</b> A recharge pit may be considered after "
        "checking soil infiltration, groundwater level, site conditions "
        "and applicable local requirements. Dimensions should be "
        "determined through a site assessment.",
        body_style,
    ))

    story.append(
        Paragraph("4. First-flush and filtration provisions", section_style)
    )

    story.append(Paragraph(
        "Provide a first-flush diverter to discard the initial roof runoff "
        "after a dry period. Install roof screens, suitable gutters and "
        "filters before water enters the storage tank. Keep the tank "
        "covered and provide a safe overflow arrangement.",
        body_style,
    ))

    story.append(Spacer(1, 12))

    story.append(Paragraph(
        "Prepared using JalSanchay — Rainwater Harvesting Assistant",
        subtitle_style,
    ))

    story.append(Paragraph(
        f"Report generated: {datetime.now().strftime('%d %B %Y, %H:%M')}",
        subtitle_style,
    ))

    document.build(story)

    buffer.seek(0)
    return buffer.getvalue()




with st.sidebar:

    st.markdown(
        """
        <div class="brand">JalSanchay</div>
        <div class="brand-subtitle">WATER RESOURCE MANAGEMENT</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    page = st.radio(
        "WORKSPACE",
        [
            "Knowledge Assistant",
            "Rainwater Calculator",
            "Design Sheet",
        ],
        label_visibility="visible",
    )

    st.markdown("---")

    st.caption("PROJECT INFORMATION")
    st.caption("AI-powered water conservation assistant")
    st.caption("Knowledge base: CGWB manuals")

    st.markdown("---")
    st.caption("JalSanchay | Checkpoint 2")




st.markdown(
    '<div class="page-heading">JalSanchay</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="page-description">'
    'Rainwater harvesting and groundwater recharge management'
    '</div>',
    unsafe_allow_html=True,
)



if page == "Knowledge Assistant":

    st.markdown(
        '<div class="section-heading">Knowledge Assistant</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Ask questions about rooftop rainwater harvesting, "
        "groundwater recharge, storage systems and water conservation."
    )

    for index, message in enumerate(st.session_state.chat_history):

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if message.get("citations"):
                display_citations(message["citations"])

            if message["role"] == "assistant":

                col1, col2, col3 = st.columns([1, 1, 8])

                with col1:
                    if st.button("Helpful", key=f"up_{index}"):
                        save_feedback(
                            message.get("question", ""),
                            message["content"],
                            "up",
                        )
                        st.success("Feedback saved.")

                with col2:
                    if st.button("Not helpful", key=f"down_{index}"):
                        save_feedback(
                            message.get("question", ""),
                            message["content"],
                            "down",
                        )
                        st.success("Feedback saved.")

    question = st.chat_input("Enter your question...")

    if question:

        st.session_state.chat_history.append({
            "role": "user",
            "content": question,
        })

        try:
            
            response = requests.post(
                f"{API_URL}/ask",
                params={
                    "q": question,
                    "top_k": 5,
                },
                timeout=120,
            )


            response.raise_for_status()

            data = response.json()
            answer, citations = extract_answer(data)

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer,
                "citations": citations,
                "question": question,
            })

            st.rerun()

        except requests.RequestException as error:
            st.error(f"Could not connect to the backend: {error}")



elif page == "Rainwater Calculator":

    st.markdown(
        '<div class="section-heading">Rooftop Rainwater Calculator</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Calculate annual rainwater collection and compare it "
        "with household water demand."
    )

    with st.form("calculator_form"):

        col1, col2 = st.columns(2)

        with col1:
            rainfall = st.number_input(
                "Annual rainfall (mm)",
                min_value=1.0,
                value=800.0,
            )

            roof_area = st.number_input(
                "Roof area (m²)",
                min_value=1.0,
                value=100.0,
            )

            roof_type = st.selectbox(
                "Roof type",
                list(ROOF_COEFFICIENTS.keys()),
            )

        with col2:
            persons = st.number_input(
                "Household members",
                min_value=1,
                value=5,
            )

            daily_demand = st.number_input(
                "Daily demand per person (litres)",
                min_value=1.0,
                value=135.0,
            )

            dry_days = st.number_input(
                "Dry period (days)",
                min_value=1,
                value=60,
            )

        calculate = st.form_submit_button(
            "Calculate rainwater potential",
            type="primary",
            use_container_width=True,
        )

    if calculate:

        calculator_inputs = {
            "rainfall_mm": rainfall,
            "roof_area_sqm": roof_area,
            "roof_type": roof_type.lower(),
            "persons": int(persons),
            "litres_per_person_per_day": daily_demand,
            "dry_days": int(dry_days),
        }

        try:
            response = requests.post(
                f"{API_URL}/agent",
                json={
                    "question": "Calculate my rooftop rainwater collection",
                    "calculator_inputs": calculator_inputs,
                    "top_k": 5,
                    "thread_id": str(uuid.uuid4()),
                    "approved": None,
                },
                timeout=120,
            )

            response.raise_for_status()
            data = response.json()

            if data.get("status") == "approval_required":

                st.session_state.pending_approval = True
                st.session_state.pending_thread_id = data["thread_id"]
                st.session_state.pending_inputs = calculator_inputs

                st.warning(
                    "Approval is required before executing the calculation."
                )

            else:
                st.session_state.calculation_result = data

        except requests.RequestException as error:
            st.error(f"Calculator request failed: {error}")

    if st.session_state.pending_approval:

        st.markdown("#### Calculation approval")

        st.write(
            "Review the submitted inputs and approve the calculation."
        )

        st.json(st.session_state.pending_inputs)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Approve calculation", type="primary"):

                try:
                    response = requests.post(
                        f"{API_URL}/agent",
                        json={
                            "question": "",
                            "calculator_inputs": None,
                            "top_k": 5,
                            "thread_id": st.session_state.pending_thread_id,
                            "approved": True,
                        },
                        timeout=120,
                    )

                    response.raise_for_status()

                    st.session_state.calculation_result = response.json()
                    st.session_state.pending_approval = False
                    st.session_state.pending_thread_id = None
                    st.rerun()

                except requests.RequestException as error:
                    st.error(f"Approval request failed: {error}")

        with col2:
            if st.button("Reject calculation"):

                try:
                    response = requests.post(
                        f"{API_URL}/agent",
                        json={
                            "question": "",
                            "calculator_inputs": None,
                            "top_k": 5,
                            "thread_id": st.session_state.pending_thread_id,
                            "approved": False,
                        },
                        timeout=120,
                    )

                    response.raise_for_status()

                    st.session_state.calculation_result = response.json()
                    st.session_state.pending_approval = False
                    st.session_state.pending_thread_id = None
                    st.rerun()

                except requests.RequestException as error:
                    st.error(f"Rejection request failed: {error}")

    if st.session_state.calculation_result:

        result_data = st.session_state.calculation_result
        answer, _ = extract_answer(result_data)

        result = result_data.get("result", {}).get("result", {})

        if result:

            st.markdown("#### Calculation results")

            c1, c2 = st.columns(2)

            with c1:
                display_metric(
                    "Annual collection",
                    f"{result.get('annual_rainwater_collection_litres', 0):,.0f} L",
                )

            with c2:
                display_metric(
                    "Household demand",
                    f"{result.get('household_demand_litres', 0):,.0f} L",
                )

            c3, c4 = st.columns(2)

            with c3:
                display_metric(
                    "Surplus / deficit",
                    f"{result.get('surplus_or_deficit_litres', 0):,.0f} L",
                )

            with c4:
                display_metric(
                    "Demand coverage",
                    f"{result.get('demand_coverage_percentage', 0):.2f}%",
                )

        else:
            st.json(result_data)



elif page == "Design Sheet":

    st.markdown(
        '<div class="section-heading">Project Design Sheet</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Prepare a one-page rooftop rainwater harvesting summary "
        "for your project documentation."
    )

    with st.form("design_form"):

        col1, col2 = st.columns(2)

        with col1:
            roof_area = st.number_input(
                "Roof area (m²)",
                min_value=1.0,
                value=100.0,
                key="pdf_roof_area",
            )

            rainfall = st.number_input(
                "Annual rainfall (mm)",
                min_value=1.0,
                value=800.0,
                key="pdf_rainfall",
            )

            roof_type = st.selectbox(
                "Roof type",
                list(ROOF_COEFFICIENTS.keys()),
                key="pdf_roof_type",
            )

        with col2:
            persons = st.number_input(
                "Household members",
                min_value=1,
                value=5,
                key="pdf_persons",
            )

            daily_demand = st.number_input(
                "Daily demand per person (litres)",
                min_value=1.0,
                value=135.0,
                key="pdf_daily_demand",
            )

            dry_days = st.number_input(
                "Dry period (days)",
                min_value=1,
                value=60,
                key="pdf_dry_days",
            )

        generate = st.form_submit_button(
            "Generate project report",
            type="primary",
            use_container_width=True,
        )

    if generate:

        coefficient = ROOF_COEFFICIENTS[roof_type]
        annual_collection = rainfall * roof_area * coefficient
        household_demand = persons * daily_demand * dry_days

        st.markdown("#### Design summary")

        c1, c2 = st.columns(2)

        with c1:
            display_metric(
                "Annual rainwater collection",
                f"{annual_collection:,.0f} litres",
            )

        with c2:
            display_metric(
                "Preliminary tank capacity",
                f"{household_demand:,.0f} litres",
            )

        st.write(f"**Runoff coefficient:** {coefficient}")
        st.write(f"**Roof type:** {roof_type}")
        st.write(
            "**Recharge pit:** Site assessment required before "
            "recommending dimensions."
        )
        st.write(
            "**First flush:** Divert initial roof runoff after dry "
            "periods before water enters the storage tank."
        )

        try:
            pdf_bytes = generate_design_sheet(
                roof_area,
                rainfall,
                roof_type,
                int(persons),
                daily_demand,
                int(dry_days),
            )

            st.download_button(
                label="Download design sheet PDF",
                data=pdf_bytes,
                file_name="JalSanchay_Design_Sheet.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            st.success("The project report is ready.")

        except Exception as error:  # noqa: BLE001
            st.error(f"PDF generation failed: {error}")




st.markdown("---")

st.markdown(
    """
    <div class="footer">
        JalSanchay | Rainwater Harvesting and Groundwater Recharge
        <br>
        Project Demonstration — Checkpoint 2
    </div>
    """,
    unsafe_allow_html=True,
)
