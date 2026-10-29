"""Create the teammate-facing work summary from recorded project evidence."""
import json
from pathlib import Path
from html import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle,getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Preformatted

ROOT=Path(__file__).resolve().parents[1]

def main():
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TitleBlue',fontName='Helvetica-Bold',fontSize=25,leading=31,textColor=colors.HexColor('#16365b'),spaceAfter=22))
    styles.add(ParagraphStyle(name='SectionBlue',fontName='Helvetica-Bold',fontSize=17,leading=22,textColor=colors.HexColor('#16365b'),spaceAfter=15))
    styles.add(ParagraphStyle(name='BodyBlue',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=10))
    styles.add(ParagraphStyle(name='CellBlue',fontName='Helvetica',fontSize=8.5,leading=11))
    styles.add(ParagraphStyle(name='HeadBlue',fontName='Helvetica-Bold',fontSize=8.5,leading=11,textColor=colors.white))
    styles.add(ParagraphStyle(name='CodeBlue',fontName='Courier',fontSize=8,leading=11,backColor=colors.HexColor('#eef3f9'),borderPadding=9,spaceAfter=14))
    story=[]
    def p(text):story.append(Paragraph(escape(text),styles['BodyBlue']))
    def heading(text):story.append(Paragraph(escape(text),styles['SectionBlue']))
    def page(title):story.append(PageBreak());heading(title)
    def table(headers,rows,widths):
        values=[[Paragraph(escape(str(c)),styles['HeadBlue']) for c in headers]]
        values +=[[Paragraph(escape(str(c)),styles['CellBlue']) for c in row] for row in rows]
        t=Table(values,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#16365b')),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#eef3f9'),colors.white]),
            ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),
            ('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
        story.extend([t,Spacer(1,14)])
    def code(text):story.append(Preformatted(text,styles['CodeBlue']))
    story.append(Spacer(1,40));heading('FLOWGUARD / TEAM HANDOFF')
    story.append(Paragraph('Work Completed<br/>and Project Transfer Guide',styles['TitleBlue']))
    p('Transformer-Based Network Intrusion Detection System for Intelligent Multi-Class Cyber Attack Classification')
    p('Prepared for teammate collaboration in Codex | 19 October 2026')
    story.append(Spacer(1,15))
    p('This document summarizes the software, experiments and submission materials created for the project. It explains how to transfer the complete folder, run the existing models on another computer and continue development in a new Codex project.')
    table(['Transfer item','Included'],[
        ['Full project ZIP','Source, trained models, sampled data, results, tests and documents'],
        ['Presentation','15-slide editable PowerPoint'],
        ['Technical report','16-page PDF with methodology and measured results'],
        ['Codex continuation','CODEX_HANDOFF.md with project map and ready-to-paste prompt'],
        ['Website/dashboard','Local Streamlit application; no public hosted URL exists']],[150,353])
    p('The package is a runnable research prototype. Physical live capture and target-network reliability remain unverified. Research simulations and recorded data experiments should not be described as production deployments.')
    page('1. Software and research work completed')
    table(['Area','Implemented work'],[
        ['Data pipeline','Pinned CIC-IDS2017 mirror downloads; source hashes/provenance; chunked audit; duplicate/conflict removal; explicit label mapping; sampled train/validation/test splits.'],
        ['Preprocessing','Training-only median imputation, signed log transform and standardization; strict input schema and invalid-value checks.'],
        ['Core classification','Five-class and seven-class trained feature-token Transformers. Seven labels include Benign, DoS, DDoS, Botnet, Port Scan, Brute Force and Infiltration.'],
        ['Controlled comparisons','Logistic Regression, Random Forest, MLP, CNN, LSTM, GRU and Transformer on matching feature split rows.'],
        ['Contextual architectures','Causal Temporal Transformer, TabTransformer, flow-grid ViT, scratch-trained BERT-style feature encoder and shared-endpoint flow GCN.'],
        ['Adaptation','Three-client local FedAvg simulation; supervised prequential online updates; Page-Hinkley loss-change detector.'],
        ['Explainability','Actual SHAP KernelExplainer and LIME Tabular integrations, plus median-replacement sensitivity.'],
        ['Packet pipeline','Passive IPv4 TCP/UDP aggregation, bounded flow storage, PCAP replay, interface-capture path and JSONL prediction events.'],
        ['User interface','Streamlit profile selector, samples/CSV upload, predictions/export, metrics, charts, Extended lab and explanation controls.'],
        ['Handoff/submission','Saved checkpoints, preprocessors, data manifests, notebook, verification logs, technical report, editable PPT, viva guide, launcher and teammate setup instructions.']],[135,368])
    p('The data sources listed in the assignment are alternatives. CIC-IDS2017 was selected; models were not trained on all listed datasets. Custom Mininet/NS-3/SDN simulation is not included.')
    page('2. Recorded experiment results')
    feature=json.loads((ROOT/'results/extended/test_metrics.json').read_text())
    table(['Seven-class model','Accuracy','Macro-F1','Benign FPR'],[
        [name,f'{m["accuracy"]:.2%}',f'{m["macro_f1"]:.4f}',f'{m["benign_false_positive_rate"]:.2%}'] for name,m in feature.items()],[188,105,105,105])
    p('Random Forest performed better than the feature Transformer in this fixed sampled benchmark. The results are retained as measured; Transformer superiority is not assumed. Infiltration has only five feature-benchmark test examples.')
    advanced=json.loads((ROOT/'results/advanced/test_metrics.json').read_text())
    table(['Context experiment','Accuracy','Macro-F1','Test outputs'],[
        [name,f'{m["accuracy"]:.2%}',f'{m["macro_f1"]:.4f}',m['test_rows']] for name,m in advanced.items()],[188,105,105,105])
    p('Temporal outputs label endpoints of nonoverlapping eight-flow windows. They differ from individual-flow evaluation rows. FedAvg and online-learning rows also have different training/adaptation protocols. These rows are not a controlled architecture ranking.')
    page('3. Verification and limits to preserve')
    p('The recorded development run passed all 22 automated tests, with no skips. The log is results/VERIFICATION.txt. Checks cover strict inputs, training-only medians, vector split separation, saved checkpoint parity, dashboard profiles, temporal inference, actual SHAP, chronological window membership, graph edges, FedAvg arithmetic, drift response and bidirectional aggregation. These checks were recorded during project development; the teammate should rerun them locally.')
    p('All 16 technical-report pages and all 15 finalized slides were rendered and visually reviewed. The PPT passed structural, layout and editable-chart checks; native Microsoft PowerPoint opening was not verified. PCAP replay processed 48 synthetic packets into 12 completed prediction events. Synthetic replay is a plumbing test, not an attack-accuracy evaluation.')
    table(['Boundary','What must not be overstated'],[
        ['Physical capture','Npcap is absent on the original machine. The interface code exists, but live-interface operation is not validated.'],
        ['Extraction shift','The custom packet statistics are not proven CICFlowMeter-equivalent; deployment accuracy is unknown.'],
        ['Temporal coverage','196 test endpoints, no infiltration endpoint, only six benign endpoints. Rare-class and false-alert evidence is weak.'],
        ['Chronology','Mirror timestamps omit AM/PM. A documented daytime correction heuristic is used; original PCAP timing was not independently checked.'],
        ['Generalization','Historical sampled data; hosts/campaigns can cross blocks; one fixed configuration/seed; no multi-dataset validation.'],
        ['Adaptation','FedAvg is a local simulation without privacy/distributed guarantees. Online updates require true labels.'],
        ['Explanations/novel attacks','Saved LIME fidelity is poor. Anomaly known-attack recall is weak. No causal explanation, zero-day reliability or new architecture claim.']],[135,368])
    page('4. Run the project on the teammate\'s computer')
    p('Extract the complete ZIP to a short path, for example C:\\Projects\\Transformer_NIDS. Install Python 3.12. Open PowerShell inside that extracted folder and run:')
    code('powershell -NoProfile -ExecutionPolicy Bypass -File .\\SETUP_PROJECT.ps1\n.\\.venv\\Scripts\\python.exe -m streamlit run app.py')
    p('Setup installs dependencies into the local .venv. Internet is required for installation. Saved models and sampled data are already included, so no training or raw-source download is needed for the demonstration. Do not transfer the original developer\'s virtual environment.')
    p('Open the URL printed in the terminal, normally http://localhost:8501. Keep the terminal open. On subsequent launches, double-click OPEN_PROJECT.cmd. Select Extended seven classes, classify the included examples, then open Extended lab for temporal/alternative models and explanations.')
    heading('Website link explained')
    p('http://127.0.0.1:8851 is the original computer\'s local server address while it is running. It cannot be shared as a remotely accessible website. On the teammate\'s computer, localhost refers to their own machine, and their server will usually print port 8501.')
    p('There is no public hosted website URL at present. A permanent shared link requires a separate hosting deployment. The supplied Streamlit application is the runnable website implementation; do not claim it has already been published.')
    heading('Optional packet demonstration')
    code('.\\.venv\\Scripts\\python.exe scripts/monitor.py --pcap \n  data/samples/synthetic_pipeline_demo.pcap')
    p('Enter the replay command on one line. Physical interface capture requires the official Npcap driver on Windows, capture permissions and target-interface testing. The application observes traffic and does not block it.')
    page('5. Continue development in Codex')
    p('Open the extracted Transformer_NIDS folder as a project in the teammate\'s Codex. The original chat history does not transfer. The handoff note, code, saved models and evidence files provide the project context.')
    heading('Ready-to-paste starting prompt')
    p('Continue this existing FlowGuard project. Read CODEX_HANDOFF.md, README.md, docs/REQUIREMENT_TRACEABILITY.md and docs/COMPLETE_PROJECT_GUIDE.md first. Inspect existing code, checkpoints, data manifests and results before editing. Set up the local environment, run the dashboard and verify the existing tests. Preserve measured results and distinguish feature classification, chronological experiments, simulations and unverified deployment claims. Use separate output folders for new experiments. Then help implement my next requested change.')
    table(['Start here','Use'],[
        ['app.py / nids/','Dashboard, model architectures, inference, capture and explanation code'],
        ['scripts/','Acquisition, preparation, training, prediction, replay and document generation'],
        ['artifacts/ / data/ / results/','Saved reference checkpoints, delivered splits, provenance and measured evidence'],
        ['CODEX_HANDOFF.md','Portable commands, file map, findings, limits and continuation prompt'],
        ['docs/','Report, PPT, summary PDF, requirement traceability, architecture and viva notes']],[170,333])
    heading('Recommended next work')
    p('First reproduce the supplied demo and tests locally. Then validate live capture/extraction parity, collect more rare attack sequences, test stronger host/campaign and external-data holdouts, evaluate realistic client heterogeneity and drift, and perform broader controlled model tuning. Public hosting is a separate task if the team wants a shared website URL.')
    p('Personalize the report and PPT with team names, registration numbers, institution and guide. Keep source attribution and measured limitations. The ZIP excludes raw-source datasets, Python environments and packet-capture drivers; download scripts and provenance are included.')
    path=ROOT/'docs/WORK_COMPLETED_AND_TEAM_HANDOFF.pdf'
    def footer(canvas,doc):
        canvas.saveState();canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#52657f'))
        canvas.drawString(46,812,'FLOWGUARD / WORK COMPLETED AND TEAM HANDOFF')
        canvas.drawString(46,25,'Prepared 19 October 2026 | Research prototype')
        canvas.drawRightString(549,25,str(doc.page));canvas.restoreState()
    SimpleDocTemplate(str(path),pagesize=A4,leftMargin=46,rightMargin=46,topMargin=54,bottomMargin=45,
        title='FlowGuard - Work Completed and Team Handoff',author='FlowGuard Project').build(story,onFirstPage=footer,onLaterPages=footer)
    print(path)

if __name__=='__main__':main()
