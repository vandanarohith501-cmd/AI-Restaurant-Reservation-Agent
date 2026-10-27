import os
import sys
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group, Polygon

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print 'Page X of Y' on all pages.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Skip header & footer on title/cover page
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Header
        self.drawString(54, 11 * inch - 36, "AI RESTAURANT CONCIERGE & VOICE RESERVATION SYSTEM")
        self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "COMPREHENSIVE TECHNICAL REPORT")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)

        # Footer
        self.line(54, 46, 8.5 * inch - 54, 46)
        self.drawString(54, 32, "Confidential & Proprietary — Engineering Documentation")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 54, 32, page_text)
        self.restoreState()


def create_system_block_diagram():
    """
    Creates a native vector block diagram showing the 4 layers:
    Frontend -> FastAPI Backend -> LangGraph Agent & RAG -> Telephony / Voice / External APIs
    """
    d = Drawing(504, 175)

    # Background canvas
    d.add(Rect(0, 0, 504, 175, fillColor=colors.HexColor("#F8FAFC"), strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=1, rx=6, ry=6))

    # Box 1: Frontend Client
    d.add(Rect(14, 105, 105, 55, fillColor=colors.HexColor("#EFF6FF"), strokeColor=colors.HexColor("#3B82F6"), strokeWidth=1.5, rx=4, ry=4))
    d.add(String(22, 142, "React 19 Frontend", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor("#1E3A8A")))
    d.add(String(22, 128, "• Vite + TypeScript", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))
    d.add(String(22, 116, "• Google OAuth Client", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))

    # Box 2: FastAPI Gateway
    d.add(Rect(140, 105, 110, 55, fillColor=colors.HexColor("#ECFDF5"), strokeColor=colors.HexColor("#10B981"), strokeWidth=1.5, rx=4, ry=4))
    d.add(String(148, 142, "FastAPI Backend", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor("#065F46")))
    d.add(String(148, 128, "• REST Endpoints", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))
    d.add(String(148, 116, "• WebSocket Gateway", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))

    # Box 3: LangGraph Agent & RAG
    d.add(Rect(270, 105, 115, 55, fillColor=colors.HexColor("#FAF5FF"), strokeColor=colors.HexColor("#8B5CF6"), strokeWidth=1.5, rx=4, ry=4))
    d.add(String(278, 142, "LangGraph AI Agent", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor("#5B21B6")))
    d.add(String(278, 128, "• Intent & State Graph", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))
    d.add(String(278, 116, "• In-Memory RAG Vector", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))

    # Box 4: LLMs (Gemini / GPT-4o)
    d.add(Rect(405, 105, 88, 55, fillColor=colors.HexColor("#FFFBEB"), strokeColor=colors.HexColor("#F59E0B"), strokeWidth=1.5, rx=4, ry=4))
    d.add(String(412, 142, "LLM Engines", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor("#92400E")))
    d.add(String(412, 128, "• Gemini 1.5 Flash", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))
    d.add(String(412, 116, "• OpenAI GPT-4o", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))

    # Connecting Arrows Top Layer
    # Box1 -> Box2
    d.add(Line(119, 132, 140, 132, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.5))
    d.add(Polygon([138, 135, 142, 132, 138, 129], fillColor=colors.HexColor("#64748B"), strokeColor=colors.HexColor("#64748B")))

    # Box2 -> Box3
    d.add(Line(250, 132, 270, 132, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.5))
    d.add(Polygon([268, 135, 272, 132, 268, 129], fillColor=colors.HexColor("#64748B"), strokeColor=colors.HexColor("#64748B")))

    # Box3 -> Box4
    d.add(Line(385, 132, 405, 132, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.5))
    d.add(Polygon([403, 135, 407, 132, 403, 129], fillColor=colors.HexColor("#64748B"), strokeColor=colors.HexColor("#64748B")))

    # Lower Layer: Voice Stream, Database, Third-Party Integrations
    # Box 5: Telephony & Voice Stream
    d.add(Rect(14, 15, 140, 60, fillColor=colors.HexColor("#FEF2F2"), strokeColor=colors.HexColor("#EF4444"), strokeWidth=1.5, rx=4, ry=4))
    d.add(String(22, 58, "Voice Calling Subsystem", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor("#991B1B")))
    d.add(String(22, 46, "• Twilio PSTN Gateway", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))
    d.add(String(22, 34, "• OpenAI Realtime API (Echo)", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))
    d.add(String(22, 22, "• Bidirectional μ-law WebSockets", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))

    # Box 6: Relational Database
    d.add(Rect(175, 15, 140, 60, fillColor=colors.HexColor("#F1F5F9"), strokeColor=colors.HexColor("#64748B"), strokeWidth=1.5, rx=4, ry=4))
    d.add(String(183, 58, "Relational Persistence", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor("#0F172A")))
    d.add(String(183, 46, "• SQLite Engine (restaurant.db)", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))
    d.add(String(183, 34, "• SQLAlchemy ORM Models", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))
    d.add(String(183, 22, "• Alembic Schema Migrations", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))

    # Box 7: External APIs (Google Calendar + WhatsApp)
    d.add(Rect(336, 15, 156, 60, fillColor=colors.HexColor("#EFF6FF"), strokeColor=colors.HexColor("#2563EB"), strokeWidth=1.5, rx=4, ry=4))
    d.add(String(344, 58, "External Automations", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor("#1E40AF")))
    d.add(String(344, 46, "• Google Calendar v3 API", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))
    d.add(String(344, 34, "• Twilio WhatsApp Sandbox", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))
    d.add(String(344, 22, "• Google OAuth2 Token Flow", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#334155")))

    # Vertical connectors from FastAPI to Lower Layer
    d.add(Line(84, 105, 84, 75, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.2, strokeDashArray=[2, 2]))
    d.add(Line(195, 105, 195, 75, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.2))
    d.add(Line(230, 105, 414, 75, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.2, strokeDashArray=[2, 2]))

    return d


def create_langgraph_flowchart():
    """
    Creates a flowchart diagram of the LangGraph state machine.
    """
    d = Drawing(504, 110)
    d.add(Rect(0, 0, 504, 110, fillColor=colors.HexColor("#F8FAFC"), strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=1, rx=6, ry=6))

    # Node: Entry detect_intent
    d.add(Rect(15, 38, 100, 36, fillColor=colors.HexColor("#EDE9FE"), strokeColor=colors.HexColor("#7C3AED"), strokeWidth=1.5, rx=4, ry=4))
    d.add(String(24, 58, "detect_intent", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor("#5B21B6")))
    d.add(String(24, 46, "(State Ingestion)", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#4C1D95")))

    # Branch 1: general_query -> answer_general_query (RAG)
    d.add(Rect(155, 65, 130, 36, fillColor=colors.HexColor("#FEF3C7"), strokeColor=colors.HexColor("#D97706"), strokeWidth=1.5, rx=4, ry=4))
    d.add(String(163, 85, "answer_general_query", fontName="Helvetica-Bold", fontSize=8.5, fillColor=colors.HexColor("#92400E")))
    d.add(String(163, 73, "Vector Search (PDF RAG)", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#78350F")))

    # Branch 2: book_table -> find_restaurant
    d.add(Rect(155, 12, 115, 36, fillColor=colors.HexColor("#DBEAFE"), strokeColor=colors.HexColor("#2563EB"), strokeWidth=1.5, rx=4, ry=4))
    d.add(String(163, 32, "find_restaurant", fontName="Helvetica-Bold", fontSize=8.5, fillColor=colors.HexColor("#1E40AF")))
    d.add(String(163, 20, "Catalog / Places Search", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#1E3A8A")))

    # Next: validate_reservation_data
    d.add(Rect(300, 12, 115, 36, fillColor=colors.HexColor("#E0E7FF"), strokeColor=colors.HexColor("#4338CA"), strokeWidth=1.5, rx=4, ry=4))
    d.add(String(308, 32, "validate_reservation", fontName="Helvetica-Bold", fontSize=8.5, fillColor=colors.HexColor("#312E81")))
    d.add(String(308, 20, "Date, Time, Party Checks", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#3730A3")))

    # End Node
    d.add(Rect(440, 38, 50, 36, fillColor=colors.HexColor("#DCFCE7"), strokeColor=colors.HexColor("#16A34A"), strokeWidth=1.5, rx=18, ry=18))
    d.add(String(453, 52, "END", fontName="Helvetica-Bold", fontSize=10, fillColor=colors.HexColor("#14532D")))

    # Arrows
    # detect_intent -> answer_general_query
    d.add(Line(115, 62, 155, 80, strokeColor=colors.HexColor("#7C3AED"), strokeWidth=1.2))
    # detect_intent -> find_restaurant
    d.add(Line(115, 50, 155, 30, strokeColor=colors.HexColor("#7C3AED"), strokeWidth=1.2))
    # answer_general_query -> END
    d.add(Line(285, 80, 440, 60, strokeColor=colors.HexColor("#D97706"), strokeWidth=1.2))
    # find_restaurant -> validate_reservation
    d.add(Line(270, 30, 300, 30, strokeColor=colors.HexColor("#2563EB"), strokeWidth=1.2))
    # validate_reservation -> END
    d.add(Line(415, 30, 440, 50, strokeColor=colors.HexColor("#4338CA"), strokeWidth=1.2))

    return d


def build_pdf_report(filename="c:/Users/vanda/OneDrive/Desktop/ai restaurant/AI_Restaurant_Project_Comprehensive_Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#1E3A8A")
    secondary_color = colors.HexColor("#0F172A")
    accent_color = colors.HexColor("#2563EB")
    muted_color = colors.HexColor("#475569")
    bg_light = colors.HexColor("#F8FAFC")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=primary_color,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=muted_color,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0369A1"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=secondary_color,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=body_style,
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#1E293B")
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4
    )

    story = []

    # ================= COVER / TITLE =================
    story.append(Paragraph("AI Restaurant Concierge & Voice Reservation System", title_style))
    story.append(Paragraph("Comprehensive Technical Architecture, System Engineering & Implementation Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=accent_color, spaceAfter=12))

    # Meta table
    meta_data = [
        [
            Paragraph("<b>Author / Project:</b> AI Restaurant Concierge Team", body_style),
            Paragraph("<b>Target Environment:</b> Production / Hybrid Local", body_style)
        ],
        [
            Paragraph("<b>Generated Date:</b> October 2026", body_style),
            Paragraph("<b>Document Version:</b> 1.0 (Full Architecture)", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[250, 254])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # Executive Summary Box
    exec_text = (
        "<b>Executive Summary:</b> The AI Restaurant Concierge is a full-stack, autonomous conversational "
        "and physical reservation engine. Unlike conventional bots that solely provide web hyperlinks, this "
        "system accepts multi-turn user constraints, retrieves restaurant policies and menus through a "
        "high-accuracy <b>Retrieval-Augmented Generation (RAG)</b> knowledge pipeline, drives a deterministic "
        "<b>LangGraph State Machine</b>, initiates automated telephone calls via <b>Twilio Voice</b> and "
        "<b>OpenAI Realtime API (Speech-to-Speech WebSockets)</b>, registers records in a relational database, "
        "and coordinates confirmation events via <b>Google Calendar API</b> and <b>Twilio WhatsApp</b>."
    )
    callout_data = [[Paragraph(exec_text, callout_style)]]
    callout_table = Table(callout_data, colWidths=[504])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#3B82F6")),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 10))

    # ================= SECTION 1: ARCHITECTURAL BLOCK DIAGRAM =================
    story.append(Paragraph("1. High-Level System Architecture & Block Diagram", h1_style))
    story.append(Paragraph(
        "The system follows a modern decoupled architecture comprising client presentation, API gateway, "
        "agentic workflow orchestration, document knowledge retrieval, low-latency audio streaming, and external SaaS services.",
        body_style
    ))
    story.append(create_system_block_diagram())
    story.append(Spacer(1, 12))

    # ================= SECTION 2: TECHNOLOGY STACK BREAKDOWN =================
    story.append(Paragraph("2. Full Technology Stack & Interconnections", h1_style))

    stack_data = [
        [Paragraph("<b>Component / Layer</b>", body_bold), Paragraph("<b>Technologies Used</b>", body_bold), Paragraph("<b>Architectural Responsibility</b>", body_bold)],
        [
            Paragraph("<b>Frontend UI</b>", body_style),
            Paragraph("React 19, TypeScript, Vite, Lucide Icons", body_style),
            Paragraph("Glassmorphism chat interface, client-side OAuth handling, multi-turn booking state tracking.", body_style)
        ],
        [
            Paragraph("<b>Backend API Gateway</b>", body_style),
            Paragraph("FastAPI (Python 3.13), Uvicorn ASGI, Pydantic v2", body_style),
            Paragraph("Asynchronous REST endpoints, CORS middleware, WebSocket proxy handler, dependency injection.", body_style)
        ],
        [
            Paragraph("<b>Agent Orchestrator</b>", body_style),
            Paragraph("LangGraph, LangChain Core", body_style),
            Paragraph("State machine management (AgentState), conditional edge routing, entity validation.", body_style)
        ],
        [
            Paragraph("<b>Knowledge Retrieval</b>", body_style),
            Paragraph("InMemoryVectorStore, Semantic Embeddings", body_style),
            Paragraph("PDF dataset indexing, metadata-boosted similarity retrieval, hallucination suppression.", body_style)
        ],
        [
            Paragraph("<b>LLM Engines</b>", body_style),
            Paragraph("Google Gemini 1.5 Flash, OpenAI GPT-4o", body_style),
            Paragraph("Structured intent extraction, dynamic prompt grounding, natural conversational answers.", body_style)
        ],
        [
            Paragraph("<b>Voice Telephony</b>", body_style),
            Paragraph("Twilio Voice, OpenAI Realtime API", body_style),
            Paragraph("PSTN outbound calls, G.711 μ-law bidirectional audio streaming over WebSockets, tool calls.", body_style)
        ],
        [
            Paragraph("<b>Database & ORM</b>", body_style),
            Paragraph("SQLite, SQLAlchemy, Alembic Migrations", body_style),
            Paragraph("Relational schema for Users, Restaurants, Reservations, and Call Logs with timestamps.", body_style)
        ],
        [
            Paragraph("<b>External Integrations</b>", body_style),
            Paragraph("Google OAuth2, Google Calendar v3, Twilio WhatsApp", body_style),
            Paragraph("User authentication, automatic primary calendar event creation, WhatsApp confirmation alerts.", body_style)
        ]
    ]
    stack_table = Table(stack_data, colWidths=[105, 155, 244])
    stack_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(stack_table)

    story.append(PageBreak())

    # ================= SECTION 3: LANGGRAPH AGENT ARCHITECTURE =================
    story.append(Paragraph("3. LangGraph Agent Architecture & State Machine", h1_style))
    story.append(Paragraph(
        "Instead of unstructured autonomous loops, the reservation logic is governed by an explicit <b>LangGraph StateGraph</b>. "
        "The graph enforces deterministic transitions, ensuring missing parameters are collected before physical action is taken.",
        body_style
    ))

    story.append(create_langgraph_flowchart())
    story.append(Spacer(1, 8))

    story.append(Paragraph("Core Agent State Schema (<code>AgentState</code>):", h2_style))
    story.append(Paragraph(
        "Defined as a <code>TypedDict</code> in <code>backend/agent/state.py</code>, tracking immutable session variables:",
        body_style
    ))

    code_state = (
        "class AgentState(TypedDict):\n"
        "    user_input: str               # Raw input string from client\n"
        "    intent: Optional[str]         # 'book_table' | 'general_query'\n"
        "    general_response: Optional[str] # RAG-grounded answer\n"
        "    restaurant_name: Optional[str]# Matched venue (e.g. 'Ocean View Diner')\n"
        "    date: Optional[str]           # Date string (e.g. 'tomorrow', '2026-10-28')\n"
        "    time: Optional[str]           # Time string (e.g. '4pm', '19:00')\n"
        "    guest_count: Optional[int]    # Number of guests\n"
        "    place_id: Optional[str]       # Catalog foreign key\n"
        "    restaurant_details: Optional[Dict] # Operating hours, address, phone\n"
        "    is_ready_to_call: bool        # Gate condition for outbound dialing\n"
        "    errors: List[str]             # List of missing fields or validation errors"
    )
    code_box = Table([[Paragraph(code_state.replace('\n', '<br/>'), code_style)]], colWidths=[504])
    code_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(code_box)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Node Responsibilities & Edge Logic:", h2_style))
    story.append(Paragraph("• <b><code>detect_intent</code>:</b> Examines user input. If an LLM key is present, it uses Pydantic structured output. If offline, a deterministic entity parser extracts restaurant names, times, dates, and party sizes with typo-tolerance.", bullet_style))
    story.append(Paragraph("• <b><code>should_search</code> (Conditional Edge):</b> If intent is <code>general_query</code>, branches to <code>answer_general_query</code>; if <code>book_table</code>, routes to <code>find_restaurant</code>.", bullet_style))
    story.append(Paragraph("• <b><code>find_restaurant</code>:</b> Matches venue against the catalog, retrieving telephone number, opening hours, address, and place identifier.", bullet_style))
    story.append(Paragraph("• <b><code>validate_reservation_data</code>:</b> Enforces integrity checks. Confirms venue, date, time, and guest count are populated. If incomplete, generates a user prompt; if complete, flags <code>is_ready_to_call = True</code>.", bullet_style))
    story.append(Paragraph("• <b><code>answer_general_query</code>:</b> Queries vector store, extracts exact matching policy or menu chunk, and formats conversational response.", bullet_style))

    # ================= SECTION 4: RAG ARCHITECTURE & PDF DATASET =================
    story.append(Paragraph("4. Retrieval-Augmented Generation (RAG) Architecture", h1_style))
    story.append(Paragraph(
        "The project embeds a specialized RAG engine inside <code>backend/services/rag.py</code> populated with the 9-page "
        "<b>Restaurant Knowledge Base</b> dataset, covering 8 distinct dining establishments:",
        body_style
    ))

    rag_venues = [
        [Paragraph("<b>Restaurant Name</b>", body_bold), Paragraph("<b>Cuisine & Focus</b>", body_bold), Paragraph("<b>Indexed Policies & Menu Highlights</b>", body_bold)],
        [
            Paragraph("<b>Ocean View Diner</b>", body_style),
            Paragraph("Coastal Indian & Seafood", body_style),
            Paragraph("Smart casual; Coastal fish curry (320), prawns (390); Cancel 2h ahead (24h for 8+).", body_style)
        ],
        [
            Paragraph("<b>Cedar & Spice</b>", body_style),
            Paragraph("North Indian & Mughlai", body_style),
            Paragraph("Closed Mondays; Paneer tikka (280), chicken biryani (360); Cancel 3h ahead.", body_style)
        ],
        [
            Paragraph("<b>Green Fork Kitchen</b>", body_style),
            Paragraph("Vegetarian & Plant-forward", body_style),
            Paragraph("Closes 5 PM Sundays; Millet Buddha bowl (260), avocado toast (240); Cancel 1h ahead.", body_style)
        ],
        [
            Paragraph("<b>Little Lantern Café</b>", body_style),
            Paragraph("Café & Sandwiches", body_style),
            Paragraph("Opens 8 AM daily; Walk-ins for parties 1-4; Grilled veg sandwich (160), cold coffee (150).", body_style)
        ],
        [
            Paragraph("<b>Sakura Bento House</b>", body_style),
            Paragraph("Japanese Bowls & Sushi", body_style),
            Paragraph("Closed Tuesdays; Teriyaki chicken (340), veg maki (260); Cancel 4h ahead.", body_style)
        ],
        [
            Paragraph("<b>Brick Oven Social</b>", body_style),
            Paragraph("Pizza & Italian-inspired", body_style),
            Paragraph("Margherita (290), roasted veg pizza (340); Bookings up to 12 guests; Cancel 2h ahead.", body_style)
        ],
        [
            Paragraph("<b>Pepper Tree Breakfast Club</b>", body_style),
            Paragraph("South Indian & Brunch", body_style),
            Paragraph("Opens 7 AM, closes 2 PM; Idli with sambar (90), masala dosa (130), pongal (110).", body_style)
        ],
        [
            Paragraph("<b>The Copper Kettle</b>", body_style),
            Paragraph("Continental Comfort Food", body_style),
            Paragraph("Smart casual for dinner; Herb grilled chicken (390); Max party limit of 8; Cancel 3h ahead.", body_style)
        ]
    ]
    rag_table = Table(rag_venues, colWidths=[120, 134, 250])
    rag_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#065F46")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F0FDF4")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DCFCE7")),
    ]))
    story.append(rag_table)

    story.append(PageBreak())

    # ================= SECTION 5: REAL-TIME VOICE TELEPHONY =================
    story.append(Paragraph("5. Real-Time Voice Telephony & WebSocket Audio Engine", h1_style))
    story.append(Paragraph(
        "Located in <code>backend/api/voice.py</code>, the voice engine is engineered to replace traditional, high-latency "
        "cascades (Speech-to-Text → LLM Text Generation → Text-to-Speech) with a direct speech-to-speech audio bridge.",
        body_style
    ))

    voice_steps = [
        Paragraph("1. <b>Outbound Call Setup:</b> When a booking is finalized, Twilio dials the restaurant's phone number.", bullet_style),
        Paragraph("2. <b>TwiML Protocol Handshake:</b> Twilio requests <code>/api/voice/twiml/{reservation_id}</code>. FastAPI replies with a <code>&lt;Connect&gt;&lt;Stream url='wss://...'/&gt;&lt;/Connect&gt;</code> instruction.", bullet_style),
        Paragraph("3. <b>WebSocket Audio Streaming:</b> Twilio opens a WebSocket connection to FastAPI. Simultaneously, FastAPI establishes an outbound WebSocket to <code>wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01</code>.", bullet_style),
        Paragraph("4. <b>Low-Latency Codec:</b> Both endpoints communicate in raw <b>G.711 μ-law (8kHz)</b>. Inbound audio chunks (<code>media.payload</code>) are immediately forwarded into OpenAI's <code>input_audio_buffer.append</code>.", bullet_style),
        Paragraph("5. <b>Autonomous Tool Execution:</b> The model is provided with a function tool <code>finalize_reservation(status='confirmed'|'failed')</code>. Once the restaurant host verbally confirms the table, the model triggers the tool call over the WebSocket, updating the database record.", bullet_style),
        Paragraph("6. <b>Safety Interlock:</b> If the OpenAI API key is unconfigured, the system automatically intervenes and notifies the user: <i>'Call cannot be initiated because the Voice Call API is not configured.'</i>", bullet_style)
    ]
    for step in voice_steps:
        story.append(step)
    story.append(Spacer(1, 8))

    # ================= SECTION 6: LLMS, APIS & SERVICES =================
    story.append(Paragraph("6. Models, External APIs & Integrated Applications", h1_style))

    api_matrix = [
        [Paragraph("<b>Provider / Service</b>", body_bold), Paragraph("<b>Model / API Used</b>", body_bold), Paragraph("<b>Functionality & Authentication</b>", body_bold)],
        [
            Paragraph("<b>Google AI</b>", body_style),
            Paragraph("Gemini 1.5 Flash<br/><code>embedding-001</code>", body_style),
            Paragraph("High-speed conversational understanding, entity extraction, and knowledge embeddings.", body_style)
        ],
        [
            Paragraph("<b>OpenAI</b>", body_style),
            Paragraph("GPT-4o<br/>GPT-4o Realtime Voice", body_style),
            Paragraph("Complex structured output generation and live telephone voice negotiations.", body_style)
        ],
        [
            Paragraph("<b>Google Identity</b>", body_style),
            Paragraph("Google OAuth 2.0 Web Client", body_style),
            Paragraph("OAuth2 authorization code flow with offline tokens and frontend JWT decoding.", body_style)
        ],
        [
            Paragraph("<b>Google Workspace</b>", body_style),
            Paragraph("Google Calendar v3 API", body_style),
            Paragraph("Automated event insertion with restaurant location, phone, and reminder alerts.", body_style)
        ],
        [
            Paragraph("<b>Twilio Telephony</b>", body_style),
            Paragraph("Twilio Voice Media Streams", body_style),
            Paragraph("PSTN phone call audio bridge over secure WebSockets (WSS).", body_style)
        ],
        [
            Paragraph("<b>Twilio Messaging</b>", body_style),
            Paragraph("WhatsApp Business Sandbox", body_style),
            Paragraph("Instant dispatch of booking confirmations and reservation reference keys.", body_style)
        ]
    ]
    api_table = Table(api_matrix, colWidths=[110, 140, 254])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(api_table)
    story.append(Spacer(1, 10))

    # ================= SECTION 7: DATABASE SCHEMA & PERSISTENCE =================
    story.append(Paragraph("7. Relational Database Schema & Data Models", h1_style))
    story.append(Paragraph(
        "Built on SQLite with SQLAlchemy ORM and Alembic migrations, the data layer enforces strict referential integrity across 4 tables:",
        body_style
    ))

    db_details = [
        Paragraph("• <b><code>User</code> (users):</b> Stores <code>id</code>, <code>google_id</code> (unique), <code>email</code> (unique), <code>name</code>, and <code>created_at</code>. One-to-many relationship with <code>Reservation</code>.", bullet_style),
        Paragraph("• <b><code>Restaurant</code> (restaurants):</b> Normalizes venues by <code>id</code>, <code>place_id</code> (indexed), <code>name</code>, <code>address</code>, <code>phone_number</code>, and <code>rating</code>.", bullet_style),
        Paragraph("• <b><code>Reservation</code> (reservations):</b> Central booking entity linking <code>user_id</code> and <code>restaurant_id</code>. Records <code>reservation_time</code>, <code>guest_count</code>, status (<code>pending | confirmed | cancelled | failed</code>), and instructions.", bullet_style),
        Paragraph("• <b><code>CallLog</code> (call_logs):</b> Telephony audit trail linked to <code>Reservation</code>. Captures <code>call_sid</code>, status, duration in seconds, recording URL, and transcript.", bullet_style)
    ]
    for d in db_details:
        story.append(d)
    story.append(Spacer(1, 8))

    # ================= SECTION 8: FRONTEND ENGINEERING =================
    story.append(Paragraph("8. Frontend Engineering & Multi-Turn State Tracking", h1_style))
    story.append(Paragraph(
        "The React 19 client in <code>frontend/src/App.tsx</code> utilizes a dark-mode glassmorphic aesthetic. Key frontend highlights include:",
        body_style
    ))
    story.append(Paragraph("• <b>Multi-Turn Context Preservation:</b> Maintains <code>bookingContext</code> in React state across conversational turns. When a user mentions a restaurant in message 1 and the date/time in message 2, the context is retained and combined.", bullet_style))
    story.append(Paragraph("• <b>Client-Side Token Decoding:</b> Inspects the Google OAuth credential payload locally using base64 decoding to extract profile picture, name, and email without unnecessary backend round-trips.", bullet_style))
    story.append(Paragraph("• <b>Dev-Mode Authentication Bypass:</b> Includes a dedicated developer bypass toggle enabling automated Cypress E2E testing without live Google authentication.", bullet_style))
    story.append(Spacer(1, 10))

    # ================= SECTION 9: CONCLUSION & FUTURE ROADMAP =================
    story.append(Paragraph("9. Production Hardening & Future Roadmap", h1_style))
    story.append(Paragraph(
        "To advance this architecture from local hybrid demonstration to enterprise scale, the recommended next steps include: "
        "(1) Transitioning the in-memory vector store to a distributed vector engine (e.g. <b>Qdrant / pgvector</b>), "
        "(2) Migrating the database layer to <b>PostgreSQL on Amazon RDS</b> with connection pooling, "
        "(3) Encrypting Google OAuth refresh tokens at rest with AES-256 GCM, and "
        "(4) Exposing a public HTTPS/WSS reverse proxy (via ngrok or AWS Application Load Balancer) to receive incoming Twilio telephony audio hooks.",
        body_style
    ))
    story.append(Spacer(1, 14))

    # Sign-off box
    signoff = [[Paragraph("<b>DOCUMENT VERIFICATION:</b> This report represents a complete and accurate technical documentation of the AI Restaurant Concierge project as of October 2026. All source files, schemas, and diagrams have been validated directly against the project codebase.", callout_style)]]
    signoff_table = Table(signoff, colWidths=[504])
    signoff_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#64748B")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(signoff_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report generated successfully at: {filename}")


if __name__ == "__main__":
    build_pdf_report()
