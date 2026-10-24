"""Build the committed PDF with reportlab (authoring-only dependency).

Run from repository root: python3 -m team.inkai.build_presentation
The Stand does not run this file or need reportlab. Numbers come from the model;
execution claims come from the checked-in verification record, never assumed.
"""
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

from .model import comparison, run

ROOT = Path(__file__).resolve().parents[2]
WIDTH, HEIGHT = 960, 540
INK = colors.HexColor("#173347")
MUTED = colors.HexColor("#526477")
BLUE = colors.HexColor("#277f91")
ORANGE = colors.HexColor("#b66b20")


def main():
    output = ROOT / "presentation.pdf"
    verification = json.loads((Path(__file__).parent / "evidence/verification.json").read_text())
    snap = comparison(28, 30)
    baseline, late = run(0), run(28)
    pdf = canvas.Canvas(str(output), pagesize=(WIDTH, HEIGHT))
    pdf.setTitle("MineMind - Representative Inkai commissioning twin")
    pdf.setAuthor("MineMind / ahsan-h-shihab")
    body = ParagraphStyle("body", fontName="Helvetica", fontSize=20, leading=28, textColor=INK)

    def text(content, x, y, width=850, size=20, color=INK):
        style = ParagraphStyle("text", parent=body, fontSize=size, leading=size * 1.35, textColor=color)
        paragraph = Paragraph(content, style)
        _, height = paragraph.wrap(width, 1000)
        paragraph.drawOn(pdf, x, y - height)
        return y - height

    def page(title, number, source="MineMind Team 118 | Representative simulation | OpenEgiz 2026"):
        pdf.setFillColor(colors.white)
        pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
        text(title, 48, 496, size=34)
        pdf.setFont("Helvetica", 10)
        pdf.setFillColor(MUTED)
        pdf.drawString(48, 22, source)
        pdf.drawRightString(WIDTH - 48, 22, str(number))

    page("MineMind", 1)
    text("JV Inkai: acid delivery timing<br/>and wellfield commissioning", 48, 408, size=38)
    text("Which new block groups start later when acid arrives late?", 48, 275, size=25)
    text("A source-informed, representative digital twin on OpenEgiz.<br/>18 twins. One adjustable scenario. Complete reset.", 48, 205, size=21)
    text("Synthetic block groups and schedules. Assumed commissioning response.<br/>No site calibration, optimizer or actual operating forecast.", 48, 111, size=16, color=MUTED)
    pdf.showPage()

    page("Connected platform and mine flows", 2)
    text("Model publisher -&gt; MQTT -&gt; Eclipse Ditto -&gt; spatial interface", 48, 421, size=24, color=BLUE)
    text("The UI reads all operating states and projections back from Ditto.<br/>Missing twins or mixed revisions produce an error, not substitute model data.", 48, 367, size=19)
    text("Commissioning acid", 48, 273, size=24)
    text("Separate area stocks -&gt; whole-dose reservation -&gt; acidification -&gt; commissioning", 48, 234, size=19)
    text("Uranium-bearing solution and product", 48, 167, size=24)
    text("Block extraction -&gt; area IX -&gt; recovered-U queue -&gt; shared MPP drying", 48, 127, size=19)
    text("Existing/sustaining acid supply is protected outside this model. Satellite transfer is aggregated.", 48, 76, size=14, color=MUTED)
    pdf.showPage()

    page("Evidence and explicit assumptions", 3, "Sources: Cameco 2024 Inkai report, printed pp.80-82; Kazatomprom 3Q24 update; PARAMETERS.md")
    text("Public facts", 48, 423, size=25, color=BLUE)
    text("MPP / Sat-1 / Sat-2 IX: 2.7 / 6.3 / 4.5 Mlb U3O8/year.<br/>Drying: 8.3 Mlb/year. Plant recovery: approximately 98%.", 48, 382, size=20)
    text("Synthetic exercise and assumptions", 48, 287, size=25, color=ORANGE)
    text("Nine group identities, positions, stocks, rates and schedules.<br/>Whole commissioning doses: 100-160 t per new group.<br/>Seven-day acidification, seven-day ramp, fixed 100 mg U/L.<br/>Annual capacities converted to uniform daily model limits.", 48, 247, size=20)
    text("The operator reported new-block acidification delays despite 106% nine-month acid fulfilment. This supports the timing mechanism, not these coefficients or a 28-day reconstruction.", 48, 105, size=15, color=MUTED)
    pdf.showPage()

    page("Accountable inventories and constraints", 4)
    text("Acid stock = initial stock + deliveries - reserved doses", 48, 416, size=24)
    text("Extracted U = dried product U + queue U + unrecovered U", 48, 346, size=24)
    text("Initial group U = remaining U + cumulative extraction", 48, 276, size=24)
    text("Area IX limits proportionally throttle extraction.<br/>Recovered uranium remains in the drying queue when packaging binds.<br/>The 2% unrecovered stream is recorded; uranium is not destroyed.", 48, 194, size=20)
    text("Conservation tests establish internal consistency, not real-world operational validation.", 48, 82, size=16, color=MUTED)
    pdf.showPage()

    page("Simulated delivery-delay comparison", 5, "Generated from model.py/config.json by build_presentation.py; no observed block data or calibration")
    text("First arrivals: day 3 -&gt; day 31 (+28 days). Second arrivals stay day 60.", 48, 426, size=19)
    left, bottom, width, height = 70, 154, 500, 195
    max_y = max(state["product_kg_u"] for state in baseline) / 1000 * 1.05
    for fraction in (0, 0.5, 1):
        y = bottom + height * fraction
        pdf.setStrokeColor(colors.HexColor("#d6dfe7"))
        pdf.line(left, y, left + width, y)
        pdf.setFont("Helvetica", 11)
        pdf.setFillColor(MUTED)
        pdf.drawRightString(left - 8, y - 4, f"{max_y*fraction:.0f}")
    for history, color in ((baseline, BLUE), (late, ORANGE)):
        path = pdf.beginPath()
        for day, state in enumerate(history):
            x = left + day / 90 * width
            y = bottom + state["product_kg_u"] / 1000 / max_y * height
            (path.moveTo if day == 0 else path.lineTo)(x, y)
        pdf.setStrokeColor(color)
        pdf.setLineWidth(2.5)
        pdf.drawPath(path)
    for day in (0, 30, 60, 90):
        pdf.setFillColor(MUTED)
        pdf.drawCentredString(left + day/90*width, bottom-20, f"Day {day}")
    text("Dried product (tonnes elemental U)", left, 375, size=14, color=MUTED)
    text("Baseline", 620, 346, width=285, size=21, color=BLUE)
    text("28-day delay", 620, 310, width=285, size=21, color=ORANGE)
    text(f"Day 30: {snap['baseline_product_kg_u']/1000:.2f} vs {snap['product_kg_u']/1000:.2f} t U.<br/>Day 90 difference:<br/>{snap['projection']['final_product_delta_kg_u']/1000:.2f} t U.", 620, 253, width=285, size=20)
    text("New B1 starts: D12 -&gt; D38.<br/>Same total acid by day 90.", 620, 141, width=285, size=17)
    text("A model outcome, not an Inkai loss estimate. Different assumptions or bottlenecks can change the difference.", 48, 83, size=15, color=MUTED)
    pdf.showPage()

    # Evidence image is an unmodified capture of our actual running Stand.
    pdf.drawImage(str(Path(__file__).parent / "evidence/delayed-spatial.png"), 48, 32, width=864, height=486, preserveAspectRatio=True, anchor="c")
    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(MUTED)
    pdf.drawString(48, 15, "Actual Stand capture | Simulated day 30, delivery delay 28 days | Synthetic blocks and geometry")
    pdf.drawRightString(WIDTH - 48, 15, "6")
    pdf.showPage()

    page("Verification and reproduction", 7)
    rows = [
        (f"{verification['unit_tests']['count']} unit tests (Windows + Ubuntu)", verification["unit_tests"]["status"]),
        ("Live MQTT / Ditto / scenario / reset", verification["live_integration"]["status"]),
        ("Original platform end-to-end smoke", verification["platform_smoke"]["status"]),
        ("Browser spatial controls", verification["browser"]["status"]),
        ("Fresh credentials and data-volume startup", verification["fresh_volume_start"]["status"]),
    ]
    y = 421
    for title, status in rows:
        text(title, 48, y, width=680, size=19)
        text(status.upper(), 760, y, width=150, size=19, color=BLUE if status == "passed" else ORANGE)
        y -= 36
    text("Start: sudo apt-get update &amp;&amp; sudo apt-get install -y make<br/>make inkai-test &nbsp; | &nbsp; make inkai &nbsp; | &nbsp; make inkai-smoke", 48, 211, size=17)
    text("Open localhost:8088. Reset -&gt; view day 30 -&gt; apply delay 28.<br/>Inspect day 38, then day 90. Reset baseline to undo completely.", 48, 142, size=18)
    text("Local test: Ubuntu 24.04 WSL2 / Docker 29.1.3 / Compose 2.40.3 / about 7 GiB RAM.<br/>Fresh-volume testing reuses downloaded images. Exact 16-GiB KVM judge reproduction remains unverified.<br/>Detailed evidence, sources, assumptions and known limitations are committed alongside the code.", 48, 78, size=12, color=MUTED)
    pdf.showPage()
    pdf.save()
    print(output)


if __name__ == "__main__":
    main()
