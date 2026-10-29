"""Print the measured report content using ReportLab (optional docs dependency)."""
from html import escape
import json
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]


def main():
    content = json.loads((ROOT / "docs/report_content.json").read_text(encoding="utf-8"))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ProjectTitle", fontName="Helvetica-Bold", fontSize=25, leading=32, textColor=colors.HexColor("#142b4b"), spaceAfter=24))
    styles.add(ParagraphStyle(name="SectionTitle", fontName="Helvetica-Bold", fontSize=17, leading=22, textColor=colors.HexColor("#173967"), spaceAfter=16))
    styles.add(ParagraphStyle(name="ReportBody", fontName="Helvetica", fontSize=10, leading=14.5, spaceAfter=10))
    styles.add(ParagraphStyle(name="TableCell", fontName="Helvetica", fontSize=8.5, leading=11))
    styles.add(ParagraphStyle(name="TableHeader", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=colors.white))
    styles.add(ParagraphStyle(name="Caption", fontName="Helvetica-Oblique", fontSize=8.5, leading=11, textColor=colors.HexColor("#52657f"), alignment=TA_CENTER, spaceAfter=12))
    pdf_path = ROOT / "docs/PROJECT_REPORT.pdf"
    document = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=46, leftMargin=46, topMargin=55, bottomMargin=48,
                                 title=content["title"], author="Computer Networks Project", subject="Implementation and measured evaluation")
    width = A4[0]-92
    story = [Spacer(1,60), Paragraph("COMPUTER NETWORKS PROJECT", styles["SectionTitle"]), Spacer(1,24),
             Paragraph(escape(content["title"]), styles["ProjectTitle"]),
             Paragraph("FlowGuard", styles["SectionTitle"]),
             Paragraph("Implementation and measured evaluation", styles["ReportBody"]), Spacer(1,36),
             Paragraph("Includes seven-class classification, chronological attention, alternative Transformers, graph and adaptation experiments, SHAP/LIME, passive packet processing and reproducible evidence.", styles["ReportBody"]),
             Spacer(1,30), Paragraph("Evaluation scope: recorded-flow experiments and tested PCAP replay. Physical live capture requires a configured driver; production and zero-day reliability remain unverified.", styles["ReportBody"]),
             Spacer(1,20), Paragraph("Personalize the cover with your name, registration number, institution and guide before submission.", styles["Caption"])]
    for section in content["sections"]:
        story.extend([PageBreak(), Paragraph(escape(section["title"]), styles["SectionTitle"])])
        for block in section["blocks"]:
            if block["type"] == "paragraph":
                story.append(Paragraph(escape(block["text"]), styles["ReportBody"]))
            elif block["type"] == "table":
                n = len(block["headers"])
                if n == 2:
                    col_widths = [width*0.40,width*0.60]
                elif n == 3:
                    col_widths = [width*0.24,width*0.34,width*0.42]
                    if block["headers"][2] == "Sampled flows":
                        col_widths = [width*0.22,width*0.60,width*0.18]
                elif n == 5:
                    col_widths = [width*0.28] + [width*0.18]*4
                else:
                    col_widths = [width/n]*n
                cells = [[Paragraph(escape(str(x)), styles["TableHeader"]) for x in block["headers"]]]
                cells += [[Paragraph(escape(str(x)), styles["TableCell"]) for x in row] for row in block["rows"]]
                t = Table(cells, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0,0),(-1,0), colors.HexColor("#173967")),
                    ("ROWBACKGROUNDS", (0,1),(-1,-1), [colors.HexColor("#edf3fa"),colors.white]),
                    ("VALIGN",(0,0),(-1,-1),"TOP"), ("LEFTPADDING",(0,0),(-1,-1),8),
                    ("RIGHTPADDING",(0,0),(-1,-1),8), ("TOPPADDING",(0,0),(-1,-1),7),
                    ("BOTTOMPADDING",(0,0),(-1,-1),7),
                    ("LINEBELOW",(0,0),(-1,0),0.5,colors.HexColor("#173967")),
                ]))
                story.extend([t, Spacer(1,12)])
            elif block["type"] == "image":
                path = (ROOT / "docs" / block["path"]).resolve()
                image = Image(str(path))
                ratio = image.imageHeight / image.imageWidth
                image.drawWidth = min(width, 440)
                image.drawHeight = image.drawWidth*ratio
                if image.drawHeight > 265:
                    image.drawWidth *= 265/image.drawHeight
                    image.drawHeight = 265
                story.extend([image, Spacer(1,5), Paragraph(escape(block["caption"]), styles["Caption"])])

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#52657f"))
        canvas.setFont("Helvetica",8)
        canvas.drawString(46, A4[1]-30, "FLOWGUARD  /  TRANSFORMER NETWORK INTRUSION DETECTION")
        canvas.drawString(46,25,"Computer Networks Project | Recorded-flow evaluation")
        canvas.drawRightString(A4[0]-46,25,str(doc.page))
        canvas.restoreState()
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Saved {pdf_path}")


if __name__ == "__main__":
    main()
