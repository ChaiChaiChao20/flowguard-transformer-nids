"""Build the current report and presentation from measured extension artifacts."""
import json
from pathlib import Path
from html import escape
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
TITLE='Transformer-Based Network Intrusion Detection System for Intelligent Multi-Class Cyber Attack Classification'

def para(text):return {'type':'paragraph','text':text}
def table(headers,rows):return {'type':'table','headers':headers,'rows':[[str(x) for x in r] for r in rows]}
def image(path,caption):return {'type':'image','path':path,'caption':caption}

def main():
    docs=ROOT/'docs';advanced=json.loads((ROOT/'results/advanced/test_metrics.json').read_text())
    extended=json.loads((ROOT/'results/extended/test_metrics.json').read_text())
    audit=json.loads((ROOT/'data/extended/processed/data_audit.json').read_text())
    temporal=json.loads((ROOT/'data/temporal/data_audit.json').read_text())
    anomaly=json.loads((ROOT/'results/extended/anomaly_metrics.json').read_text())
    replay=json.loads((ROOT/'results/pcap_replay.summary.json').read_text())
    shapmeta=json.loads((ROOT/'results/explanations/shap.json').read_text())
    limemeta=json.loads((ROOT/'results/explanations/lime.json').read_text())
    classes=temporal['classes'];tm=extended['Transformer'];seq=advanced['TemporalTransformer']
    comparison=pd.read_csv(ROOT/'results/extended/model_comparison.csv')
    winner=comparison.loc[comparison.macro_f1.idxmax()]
    plots=ROOT/'results/advanced/plots';plots.mkdir(parents=True,exist_ok=True)
    for name,m in advanced.items():
        fig,ax=plt.subplots(figsize=(8,6));matrix=m['confusion_matrix'];im=ax.imshow(matrix,cmap='Blues')
        ax.set(xticks=range(7),yticks=range(7),xticklabels=classes,yticklabels=classes,xlabel='Predicted',ylabel='Actual',title=name+' | chronological episode split')
        ax.tick_params(axis='x',labelrotation=40)
        for i in range(7):
            for j in range(7):ax.text(j,i,str(matrix[i][j]),ha='center',va='center',color='white' if matrix[i][j]>max(map(max,matrix))/2 else 'black')
        fig.colorbar(im,ax=ax);fig.tight_layout();fig.savefig(plots/f'{name}_confusion.png',dpi=130);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,5));names=list(advanced)
    ax.bar(names,[advanced[n]['macro_f1'] for n in names],color='#2563eb')
    ax.set(ylim=(0,1.05),ylabel='Macro-F1 across all seven labels',title='Context experiments: differing output units and adaptation protocols')
    ax.tick_params(axis='x',labelrotation=25);fig.tight_layout();fig.savefig(plots/'comparison.png',dpi=130);plt.close(fig)
    sections=[]
    def section(title,*blocks):sections.append({'title':title,'blocks':list(blocks)})
    section('1. Abstract and delivered scope',
        para('FlowGuard implements multi-class network intrusion classification with Transformer attention, chronological flow windows, network context, alternative attention models, graph learning, supervised adaptation and explainability. The local dashboard exposes saved models and measured evidence. A passive packet pipeline converts IPv4 TCP/UDP PCAP or interface traffic to completed flows and JSONL prediction events.'),
        para(f'The seven-class feature Transformer achieved accuracy {tm["accuracy"]:.2%}, macro-F1 {tm["macro_f1"]:.4f} and benign false-positive rate {tm["benign_false_positive_rate"]:.2%}. {winner["model"]} achieved the highest macro-F1 ({winner["macro_f1"]:.4f}) in that declared benchmark. Temporal attention achieved accuracy {seq["accuracy"]:.2%} on {seq["test_rows"]} window endpoints, with no held-out infiltration window. These experiments measure historical sampled data, not production or zero-day reliability.'),
        table(['Capability','Delivered evidence'],[
            ['Seven traffic classes','Benign, DoS, DDoS, Botnet, Port Scan, Brute Force, Infiltration'],
            ['Attention architectures','Feature Transformer, temporal encoder, TabTransformer, flow-grid ViT, BERT-style encoder'],
            ['Research extensions','Shared-endpoint GCN, local FedAvg, label-gated online updates, loss drift detector'],
            ['Explainability','SHAP KernelExplainer, LIME Tabular, median-replacement sensitivity'],
            ['Network pipeline','PCAP replay tested; physical live capture requires Npcap and remains unverified'],
            ['Deliverables','Code, data samples, checkpoints, results, dashboard, report, slides, viva and tests']]),
        para('Add student/team names, registration numbers, institution, guide and required declaration before submission. Dataset and architecture choices are acknowledged rather than presented as invented research.'))
    section('2. Network problem and objectives',
        para('A bidirectional flow groups packets by endpoints, ports and protocol. Duration, direction, packet-size variation, inter-arrival times, byte/packet rates and TCP flags describe exchange behavior. DoS, DDoS, bot activity and scans may share flow statistics, so context across traffic can matter. FTP/SSH brute-force labels and infiltration labels add harder and rarer classes.'),
        para('The objectives are to implement attention-based classification, compare traditional and neural baselines, test chronological feature context, expose explainable predictions, and integrate passive packet-to-flow processing. Each objective is accompanied by measured artifacts or an explicit runtime boundary. A supervised classifier still learns known labels; unusual traffic cannot automatically be called a novel attack.'),
        para('The deployment path is a mirrored or monitored interface, passive packet collection, bounded flow aggregation, saved preprocessing, model inference and an alert log. Flow closing and idle/active timeout add latency. No traffic blocking or attack generation is part of this IDS.'))
    section('3. Data acquisition, labels and audit',
        para(f'The extended feature benchmark audited {audit["original_rows"]:,} rows across six pinned c01dsnap/CIC-IDS2017 mirror CSVs. The contextual source contains {temporal["source_rows"]:,} rows from rdpahalavan/CIC-IDS2017, revision {temporal["revision"]}. Its SHA-256 is recorded in data/temporal/data_audit.json and checked by download/preparation scripts. Mirrors were not independently verified against original UNB PCAP files.'),
        table(['Class','Feature sample','Train / validation / test'],[
            [c,audit['sample_counts'][c],f"{audit['splits']['train'][c]} / {audit['splits']['validation'][c]} / {audit['splits']['test'][c]}"] for c in classes]),
        para('DoS subtypes are grouped as DoS, Bot becomes Botnet, PortScan becomes Port Scan, and FTP-Patator/SSH-Patator become Brute Force. Unsupported labels are excluded, never silently relabeled Benign. Numeric-vector duplicates and conflicting labels are removed before splitting. Uniform class sampling modifies traffic prevalence.'),
        para('Infiltration has only 34 selected feature vectors: 24 training, five validation and five test. A high score on five test examples is statistically weak. The listed assignment datasets are alternatives; this project uses CIC-IDS2017 and does not claim multi-dataset validation.'))
    section('4. Preprocessing and split discipline',
        para('The feature benchmark uses 70/15/15 stratified random partitions after vector deduplication. Median imputation, signed log1p transformation and standardization are fitted only on training rows. The core five-class benchmark remains available as a reference. Related sessions may remain across those random partitions.'),
        para('The contextual sample contains 15,574 unique selected-feature vectors. Source/day streams are separated into activity episodes using a 300-second idle gap. Each episode is split into chronological 70/15/15 blocks. Eight-flow windows never cross a split, source, day or idle gap; windows do not overlap. Sampling preserves timestamp order but omits intervening flows. Hosts/campaigns may still occur in several blocks.'),
        para('The mirror encodes 12-hour clocks without AM/PM. A working-day heuristic shifts hours 01..07 by 12 hours, correcting 1,470,484 source timestamps. This assumption is recorded in the audit and has not been independently checked against original packets. Chronological conclusions depend on it.'),
        table(['Class','Context train / validation / test','Temporal test endpoints'],[
            [c,' / '.join(str(temporal['flow_counts'][s].get(c,0)) for s in ['train','validation','test']),temporal['sequence_endpoint_counts']['test'].get(c,0)] for c in classes]))
    section('5. Inputs and network context',
        para('The base schema contains 24 duration, packet count/length, throughput, inter-arrival and TCP-flag statistics. See data/processed/feature_dictionary.csv for names, units and meanings. Extra labels are not prediction inputs. Invalid strings, missing columns and wholly unusable rows are rejected; missing cells use saved training medians.'),
        table(['Additional input','Encoding and boundary'],[
            ['Source and destination port','Numeric 0..65535, log-scaled with other numeric inputs'],
            ['Protocol','Unknown=0, TCP=1, UDP=2, ICMP=3; categorical tokens in TabTransformer'],
            ['Source and destination IP','Private-status indicators and deterministic CRC32 buckets mod 256'],
            ['Raw IP addresses','Used for chronological host grouping and graph edges, not unbounded numeric addresses'],
            ['Connection state','OPEN/CLOSED/RESET proxy inferred from FIN/RST counts; not full TCP reassembly'],
            ['Timestamp','ISO local capture clock; used to order windows, not a predictive schedule feature']]),
        para('Context models receive 32 numerical inputs. TabTransformer also receives protocol/state categorical tokens. IP buckets collide and can encode dataset-specific topology, so cross-network testing is essential.'))
    section('6. Transformer and baseline implementations',
        table(['Model','Representation'],[
            ['Feature Transformer','Per-feature affine tokenization, CLS, two encoder layers, four heads, dimension 32'],
            ['Logistic Regression / Random Forest','Standardized 24-feature inputs; balanced class weights'],
            ['MLP / CNN','Dense reference / convolutions over fixed feature order'],
            ['LSTM / GRU','Recurrence over fixed feature order, not time'],
            ['BERT-style encoder','Bidirectional feature tokens + CLS, trained from scratch on 32 context features'],
            ['TabTransformer','Contextual attention over protocol/state embeddings concatenated with numerical features'],
            ['Flow-grid ViT','Four-value numerical patches, learned positions, CLS, vision-style Transformer']]),
        para('BERT-style describes an encoder architecture; it does not mean pretrained NLP BERT or masked-language pretraining. Flow-grid ViT uses numerical flow patches rather than screenshots or packet images. These representation choices are reproducible alternatives, not new architecture claims.'),
        para('Feature benchmark neural training uses AdamW, learning rate .001, batch 256, weighted cross-entropy, gradient clipping 1, maximum 18 epochs and validation macro-F1 selection. Advanced architectures use batch 128, maximum ten epochs, early-stop patience four and one fixed configuration/seed. Parameter counts differ; the experiments are not exhaustive capacity-matched comparisons.'))
    section('7. Seven-class benchmark results',
        table(['Model','Accuracy','Macro-F1','Benign FPR'],[
            [r.model,f'{r.accuracy:.2%}',f'{r.macro_f1:.4f}',f'{r.benign_false_positive_rate:.2%}'] for r in comparison.itertuples()]),
        image('../results/extended/plots/model_comparison.png','Measured seven-class feature benchmark; identical sampled random-split rows.'),
        para(f'The feature Transformer selected epoch {tm["best_epoch"]}; accuracy was {tm["accuracy"]:.2%}. The report preserves the stronger Random Forest result rather than assuming attention improves every metric. Per-class reports, error flows, confusion matrices and training histories are in results/extended/. Single-seed historical scores do not establish operational superiority.'))
    section('8. Chronological Temporal Transformer',
        para('A linear projection turns each contextual flow into a 32-dimensional token. Learned time positions and a causal attention mask connect earlier observations to the last flow. Two Transformer layers and a seven-class head classify the endpoint of a complete eight-flow window. No future flow within the window may influence an earlier hidden position.'),
        para(f'The frozen temporal model was evaluated on {seq["test_rows"]} endpoints: accuracy {seq["accuracy"]:.2%}, macro-F1 across all seven labels {seq["macro_f1"]:.4f}. Infiltration has zero temporal test support and benign has only six endpoints. Do not infer dependable infiltration detection or a stable benign false-positive estimate from this evaluation.'),
        image('../results/advanced/plots/TemporalTransformer_confusion.png','Temporal confusion counts; the empty infiltration row is an evaluation gap.'),
        para('Temporal outputs differ from individual-flow outputs; their aggregate scores are not a like-for-like model ranking. Unit tests verify influence of history, timestamp ordering, idle-gap boundaries and disjoint window membership. Eight-flow context demonstrates sequence attention but does not prove all long-range traffic relationships are captured.'))
    section('9. Context models and graph experiment',
        table(['Model','Accuracy','Macro-F1','Test outputs'],[
            [n,f'{m["accuracy"]:.2%}',f'{m["macro_f1"]:.4f}',m['test_rows']] for n,m in advanced.items()]),
        para('The graph experiment treats flows as nodes and creates edges when either endpoint IP matches an endpoint of another flow in the same consecutive 128-flow batch. Self loops and symmetric degree normalization feed a two-layer GCN. Graph construction never links different data splits. Predictions depend on supplied batch context, so a flow can receive different predictions in a different graph.'),
        para('The chronological individual-flow tests contain seven infiltration examples; the temporal endpoint test contains none. Seven-label macro-F1 explicitly includes zero-support labels. The FedAvg and online rows have different training/adaptation protocols and should not be presented as controlled architecture rankings. Confusion matrices and saved checkpoint parity evidence accompany these results.'))
    section('10. Federated and online-learning extensions',
        para('FedAvg partitions contextual training examples across three simulated IID clients. Each round runs two local epochs and aggregates model tensors weighted by client sample counts. Three fixed rounds produce a saved federated checkpoint. All clients execute locally; there is no distributed transport, secure aggregation, differential privacy or privacy guarantee.'),
        table(['Round','Validation macro-F1'],[[r['round'],f"{r['validation_macro_f1']:.4f}"] for r in json.loads((ROOT/'results/advanced/federated_rounds.json').read_text())]),
        para('Online learning starts from the validation-selected contextual encoder. Each chronological validation chunk is predicted before labels are revealed. One supervised update follows at a fixed .0001 learning rate. A Page-Hinkley detector observes chunk loss increases. The final adapted model is frozen and scored on test flows. Unverified predictions are not used as ground truth.'),
        para('Prequential accuracy/loss/drift records are saved in results/advanced/online_prequential.csv. Drift arithmetic and weighted aggregation are tested, but real client heterogeneity and real-world concept drift remain unvalidated.'))
    section('11. SHAP, LIME and anomaly flags',
        para(f'SHAP KernelExplainer uses 20 training reference rows and 128 coalition samples for the saved example. Reference probability {shapmeta["expected_probability"]:.6f} plus attribution sum {shapmeta["attribution_sum"]:.6f} reconstructs predicted {shapmeta["predicted_class"]} probability {shapmeta["predicted_probability"]:.6f}. The raw attribution CSV is in results/explanations/shap.csv.'),
        para(f'LIME Tabular uses 1,000 local perturbations and reports conditional feature weights. Its saved local-surrogate R-squared is {limemeta["local_surrogate_r2"]:.4f}, which is poor fidelity; those weights should not support strong explanations. Both methods can be affected by correlated features and unrealistic perturbations. Median replacement remains a simpler sensitivity view. None is a causal explanation.'),
        para(f'A benign-trained Isolation Forest adds anomaly_score and atypical_flag to extended-profile predictions. Its threshold is the validation-benign 99th percentile. Test benign false-alert rate is {anomaly["test_benign_false_alert_rate"]:.2%}; known-attack anomaly recall is only {anomaly["test_known_attack_anomaly_recall"]:.2%}. This weak result is preserved, and the atypicality flag is not presented as zero-day detection.'),
        para('The dashboard computes actual SHAP/LIME explanations for the first held-out sample in the selected profile. Optional dependencies are listed in requirements-extensions.txt. Inputs are imputed with saved training medians before explanation.'))
    section('12. Passive capture, replay and latency',
        para('monitor.py uses Scapy to read PCAP packets or passively sniff an interface. The bounded aggregator groups IPv4 TCP/UDP by bidirectional five-tuples, retains packet sizes/times rather than payload, and closes on FIN/RST, idle/active timeout or packet cap. Events contain network metadata, flow statistics, class probabilities, attack flag and anomaly score. A JSONL log is flushed after prediction batches.'),
        para(f'The synthetic plumbing test contains 48 packets and emits {replay["flows"]} completed flows. Measured runtime was {replay["elapsed_seconds"]:.3f} seconds ({replay["flows_per_second"]:.1f} flows/second), including extraction, inference and output on this tiny file. This is a small functional test, not a production throughput benchmark; no attack ground truth is attached.'),
        para('The custom extractor uses IP packet lengths, population standard deviations and per-packet flag counts. Its semantics differ from CICFlowMeter. Completed-flow closing delays and feature shift prevent an inference timing result from proving real-time detection accuracy. Validate extraction equivalence, queue load and target-network false alerts before deployment.'),
        para('Npcap is absent on this Windows computer. The interface capture path is implemented, but physical live capture could not be validated. Install the official driver, obtain capture permissions, list interfaces, run a bounded capture and review the events as documented in COMPLETE_PROJECT_GUIDE.md. IPv6 and fragmented transport reassembly are not implemented.'))
    section('13. Verification, demonstration and reproduction',
        para('Automated checks cover strict inputs, training-only preprocessing, vector split separation, checkpoint parity, the original dashboard, extended profile and advanced model dashboard, temporal window membership, chronological boundaries, graph-edge influence, model output dimensions, FedAvg arithmetic, drift response and bidirectional packet aggregation. The full recorded verification output is results/VERIFICATION.txt.'),
        para('Open OPEN_PROJECT.cmd; select Extended seven classes and classify included samples. Inspect model performance and per-class confusion counts. Open Extended lab, run a temporal/context model, compute SHAP/LIME, then replay the synthetic PCAP with monitor.py. The CSV demonstration includes at most ten held-out examples per class and is not a representative benchmark.'),
        para('Source downloads are pinned by revision and hashes. Raw source files and virtual environments are excluded from the ZIP, while sampled data, saved preprocessing, checkpoints, labels, manifests and measured outputs are included. README documents preparation/training commands. Requirements-lock.txt records the tested environment. Model-only timings exclude capture/extraction; replay timing includes its pipeline work.'))
    section('14. Conclusions and limits',
        para('The delivered project implements the principal Transformer NIDS, comparative models, chronological attention, contextual inputs, optional architecture variants, explainability, graph learning and supervised adaptation. A passive packet pipeline is runnable for PCAP replay and provides an interface capture path. Reported results are measured rather than invented.'),
        para('Remaining validation concerns are physical live capture on a configured driver, extraction/domain-shift accuracy, independently verified original timestamps, stronger host/campaign holdouts, more rare infiltration sequences, multiple seeds/configurations, realistic federated clients and observed concept drift. A deployable production IDS, superior Transformer performance, research novelty and zero-day reliability have not been established.'),
        para('The supplied research-gap/novelty statements are hypotheses and motivation. The experiment is a reproducible implementation of established ideas, with explicit evaluation boundaries. Institution-specific cover pages, approval, submission rules and student identity still require personalization.'))
    references=[
        'Sharafaldin, Lashkari and Ghorbani (2018). Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization. https://www.unb.ca/cic/datasets/ids-2017.html',
        'Vaswani et al. (2017). Attention Is All You Need. https://arxiv.org/abs/1706.03762',
        'Gorishniy et al. (2021). Revisiting Deep Learning Models for Tabular Data. https://arxiv.org/abs/2106.11959',
        'Huang et al. (2020). TabTransformer. https://arxiv.org/abs/2012.06678',
        'Dosovitskiy et al. (2020). An Image Is Worth 16x16 Words. https://arxiv.org/abs/2010.11929',
        'Devlin et al. (2018). BERT. https://arxiv.org/abs/1810.04805',
        'Kipf and Welling (2016). Semi-Supervised Classification with Graph Convolutional Networks. https://arxiv.org/abs/1609.02907',
        'McMahan et al. (2016). Communication-Efficient Learning of Deep Networks from Decentralized Data. https://arxiv.org/abs/1602.05629',
        'Ribeiro et al. (2016). Why Should I Trust You? https://arxiv.org/abs/1602.04938',
        'Lundberg and Lee (2017). A Unified Approach to Interpreting Model Predictions. https://arxiv.org/abs/1705.07874',
        'SHAP KernelExplainer documentation. https://shap.readthedocs.io/en/stable/generated/shap.KernelExplainer.html',
        'Scapy capture documentation. https://scapy.readthedocs.io/en/stable/usage.html ; Npcap: https://npcap.com/']
    section('15. References and acknowledgements',*[para(x) for x in references])
    content={'title':TITLE,'subtitle':'FlowGuard | Extended implementation and measured evaluation','sections':sections}
    (docs/'report_content.json').write_text(json.dumps(content,indent=2))
    md=['# '+TITLE,'',content['subtitle'],'']
    for s in sections:
        md+=['## '+s['title'],'']
        for block in s['blocks']:
            if block['type']=='paragraph':md +=[block['text'],'']
            elif block['type']=='table':
                md+=['| '+' | '.join(block['headers'])+' |','| '+' | '.join(['---']*len(block['headers']))+' |']
                md+=['| '+' | '.join(r)+' |' for r in block['rows']];md+=['']
            else:md +=[f"![{block['caption']}]({block['path']})",'']
    (docs/'PROJECT_REPORT.md').write_text('\n'.join(md),encoding='utf-8')
    def slide(title,body,notes=''):return {'title':title,'body':body,'notes':notes}
    slides=[{'title':'Transformer-Based Network Intrusion Detection System','subtitle':'Intelligent Multi-Class Cyber Attack Classification','notes':TITLE+'; add student and institutional details.'},
        slide('Scope of the completed implementation',['Seven-class flow classifier and controlled baselines','Chronological attention and endpoint graph context','TabTransformer, flow-grid ViT and BERT-style encoder','SHAP/LIME, FedAvg and supervised online learning','Passive PCAP pipeline; live interface path provided']),
        slide('Network inputs',['24 flow statistics: duration, sizes, rates, intervals and flags','Context: source/destination ports and protocol','IP private-status indicators and stable hash buckets','Raw IPs form host windows and shared-endpoint graphs','Connection state is a FIN/RST-derived proxy']),
        slide('Data and evaluation',['Six pinned CIC-IDS2017 CSVs for the seven-class benchmark','34 unique infiltration samples; only five feature test rows','Context sample: 15,574 flows with timestamps and endpoints','Chronological activity blocks and disjoint eight-flow windows','AM/PM correction assumption is recorded in the audit']),
        slide('Attention architecture',['Feature encoder: value tokens, feature identities and CLS','Temporal encoder: chronological flows and a causal mask','TabTransformer: contextual protocol/state categories','Flow-grid ViT: numeric patches with learned positions','BERT-style means scratch-trained bidirectional feature attention']),
        slide('Training and comparison',['Logistic Regression, Random Forest, MLP, CNN, LSTM, GRU','Feature Transformer on identical seven-class split rows','Training-only medians, signed log transform and scaling','Validation selects checkpoints; no test-driven tuning','Fixed configurations and one seed limit broad conclusions']),
        {'title':'Seven-class benchmark','subtitle':f'Highest observed macro-F1: {winner["model"]} ({winner["macro_f1"]:.4f})','chart':{'categories':comparison.model.tolist(),'values':comparison.macro_f1.tolist()},'notes':'results/extended/model_comparison.csv; sampled random split. Five infiltration test examples. No production claim.'},
        slide('Chronological Temporal Transformer',[f'Test endpoints: {seq["test_rows"]} nonoverlapping eight-flow windows',f'Accuracy {seq["accuracy"]:.2%}; seven-label macro-F1 {seq["macro_f1"]:.4f}','No future flows enter the causal window','No held-out infiltration window; six benign endpoints','Different output rows from the individual-flow benchmark'],'Timestamp AM/PM heuristic and sampled-flow gaps constrain chronology; hosts/campaigns may cross blocks.'),
        slide('Graph and alternative models',['GCN connects flows sharing an endpoint in one batch','Graph construction does not cross train/test boundaries','TabTransformer contextualizes categorical embeddings','ViT processes a numerical flow grid, not packet images','Saved models and measured predictions are in Extended lab']),
        slide('Federated and online extensions',['FedAvg: three local simulated clients, three fixed rounds','Client updates weighted by training sample count','Online stream: predict, reveal true labels, then update','Page-Hinkley monitors increases in observed chunk loss','No distributed privacy or unlabeled adaptation claim']),
        slide('Explainable predictions',['Actual SHAP KernelExplainer and LIME Tabular integrations','SHAP reports its reference probability and additive sum',f'LIME example surrogate R-squared: {limemeta["local_surrogate_r2"]:.3f} — weak fidelity','Feature sensitivity remains available for individual flows','Explanations describe model behavior, not causal attack evidence']),
        slide('Passive capture and replay',['IPv4 TCP/UDP packets → bounded bidirectional flows','Completed flows → seven-class predictions → JSONL events',f'Tested replay: {replay["flows"]} synthetic flows; no attack ground truth','Physical capture requires Npcap; not validated here','Custom extraction differs from CICFlowMeter semantics']),
        slide('Open and demonstrate',['Double-click OPEN_PROJECT.cmd and keep the terminal open','Select Extended seven classes; classify included samples','Inspect comparisons and per-class confusion matrices','Use Extended lab for temporal models and SHAP/LIME','Replay the included PCAP with scripts/monitor.py']),
        slide('Measured findings and boundaries',[f'Seven-class Transformer accuracy: {tm["accuracy"]:.2%}',f'Random Forest macro-F1: {winner["macro_f1"]:.4f}; report the observed winner','Rare classes, topology and historical sampling limit reliability','Anomaly scoring is weak and does not prove zero-day detection','Next validation: live driver, extraction parity and external data']),
        slide('References and contribution',['Reproducible implementation, trained artifacts and local demo','CIC-IDS2017: Sharafaldin, Lashkari and Ghorbani','Attention, tabular, vision, graph and FedAvg methods acknowledged','SHAP/LIME citations and complete evidence in the report','Student identity and submission format need personalization'],'Full bibliography in PROJECT_REPORT.md; original architecture papers and official Scapy/SHAP docs are linked.')]
    (docs/'slide_content.json').write_text(json.dumps(slides,indent=2),encoding='utf-8')
    html=['<!doctype html><html><head><meta charset="utf-8"><title>FlowGuard</title><style>body{font:22px Arial;background:#10233f;color:white;margin:0}section{min-height:85vh;padding:6vh 7vw;border-bottom:1px solid #557}h1{font-size:44px}li{line-height:1.7;margin:12px 0}img{max-width:80%;background:white}footer{color:#a9c9ed}</style></head><body>']
    for i,s in enumerate(slides):
        body='<img src="../results/extended/plots/model_comparison.png" alt="Measured seven-class results">' if 'chart' in s else '<ul>'+''.join('<li>'+escape(x)+'</li>' for x in s.get('body',[]))+'</ul>'
        html.append(f'<section><h1>{escape(s["title"])}</h1><p>{escape(s.get("subtitle",""))}</p>{body}<footer>{i+1} / {len(slides)}</footer></section>')
    (docs/'PRESENTATION.html').write_text(''.join(html)+'</body></html>',encoding='utf-8')
    print('Generated extended measured report, plots, slide source and browser presentation')

if __name__=='__main__':main()
