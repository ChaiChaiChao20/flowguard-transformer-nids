import unittest
import numpy as np
import torch
import json
from pathlib import Path
import pandas as pd
from nids.advanced_models import TemporalTransformer,FlowViT,TabTransformer,FlowGraphNetwork
from nids.adaptation import fedavg,PageHinkley
from nids.capture import FlowAggregator


class ExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):torch.set_num_threads(4)
    def test_temporal_last_flow_depends_on_history(self):
        torch.manual_seed(42);model=TemporalTransformer(24,5).eval()
        a=torch.zeros(1,8,24);b=a.clone();b[:,0]=10
        with torch.inference_mode():
            self.assertFalse(torch.allclose(model(a),model(b)))
        with self.assertRaises(ValueError):model(torch.zeros(1,9,24))

    def test_patch_and_category_models(self):
        x=torch.randn(3,24)
        self.assertEqual(FlowViT(24,7)(x).shape,(3,7))
        self.assertEqual(TabTransformer(24,7)(x,torch.zeros(3,2,dtype=torch.long)).shape,(3,7))

    def test_graph_edges_change_prediction(self):
        torch.manual_seed(42);model=FlowGraphNetwork(24,5).eval();x=torch.randn(3,24)
        self.assertFalse(torch.allclose(model(x,torch.eye(3)),model(x,torch.ones(3,3))))

    def test_fedavg_weighted_by_samples(self):
        result=fedavg([{'w':torch.tensor([1.])},{'w':torch.tensor([5.])}],[1,3])
        self.assertAlmostEqual(result['w'].item(),4)

    def test_drift_loss_increase(self):
        detector=PageHinkley(threshold=1)
        self.assertFalse(any(detector.update(.1) for _ in range(20)))
        self.assertTrue(any(detector.update(2.) for _ in range(5)))

    def test_bidirectional_flow_and_timeout(self):
        from scapy.all import IP,TCP,Raw
        agg=FlowAggregator(idle_timeout=1)
        packets=[IP(src='10.0.0.1',dst='10.0.0.2')/TCP(sport=1000,dport=80,flags='S'),
                 IP(src='10.0.0.2',dst='10.0.0.1')/TCP(sport=80,dport=1000,flags='SA')/Raw(b'abc')]
        for i,p in enumerate(packets):p.time=10+i*.25;self.assertEqual(agg.consume(p),[])
        rows=agg.expire(12);self.assertEqual(len(rows),1);r=rows[0]
        self.assertEqual(r['Total Fwd Packets'],1);self.assertEqual(r['Total Backward Packets'],1)
        self.assertEqual(r['Flow Duration'],250000);self.assertEqual(r['SYN Flag Count'],2)
        self.assertEqual(r['Flow IAT Mean'],250000);self.assertEqual(r['Destination Port'],80)
        self.assertTrue(all(np.isfinite(r[k]) for k in ['Flow Bytes/s','Average Packet Size']))

    def test_packet_and_flow_memory_bounds(self):
        from scapy.all import IP,UDP
        agg=FlowAggregator(max_packets=2,max_flows=1)
        p=IP(src='10.0.0.1',dst='10.0.0.2')/UDP(sport=1,dport=2);p.time=1
        self.assertEqual(agg.consume(p),[]);p.time=2
        self.assertEqual(len(agg.consume(p)),1);self.assertEqual(len(agg.flows),0)

    def test_temporal_split_windows_have_no_shared_members(self):
        root=Path(__file__).resolve().parents[1]
        data=np.load(root/'data/temporal/splits.npz')
        frame=pd.read_csv(root/'data/temporal/sample_manifest.csv')
        pools=[]
        for split in ['train','validation','test']:
            members=data['sequence_members_'+split];pools.append(set(members.flatten()))
            self.assertEqual(len(members.flatten()),len(pools[-1]))
            for ids in members:
                rows=frame.iloc[ids]
                self.assertTrue(rows.split.eq(split).all());self.assertEqual(rows.source_ip.nunique(),1)
                times=pd.to_datetime(rows.time)
                self.assertTrue(times.is_monotonic_increasing)
                self.assertTrue(times.diff().dt.total_seconds().dropna().le(300).all())
        self.assertFalse(pools[0]&pools[1]);self.assertFalse(pools[0]&pools[2]);self.assertFalse(pools[1]&pools[2])

    def test_context_preprocessor_training_medians(self):
        import joblib
        from nids.context import context_features
        root=Path(__file__).resolve().parents[1]
        frame=pd.read_csv(root/'data/temporal/train_flows.csv')
        pre=joblib.load(root/'data/temporal/preprocessor.joblib')
        np.testing.assert_allclose(pre.named_steps['impute'].statistics_,context_features(frame).median().to_numpy(),equal_nan=True)

    def test_all_advanced_saved_predictions_match_fresh_inference(self):
        from nids.advanced_inference import AdvancedPredictor
        root=Path(__file__).resolve().parents[1]
        frame=pd.read_csv(root/'data/temporal/test_flows.csv')
        meta=json.loads((root/'artifacts/advanced/model_metadata.json').read_text())
        for name in meta['models']:
            with self.subTest(model=name):
                pred=AdvancedPredictor(root/'artifacts/advanced',name).predict(frame)
                self.assertTrue(np.isfinite(pred.model_probability).all())
                if (root/f'results/advanced/{name}_predictions.csv').exists():
                    saved=pd.read_csv(root/f'results/advanced/{name}_predictions.csv')
                    self.assertEqual(pred.predicted_class.tolist(),saved.predicted.tolist())
                    np.testing.assert_allclose(pred.model_probability,saved.probability,atol=1e-6)

    def test_extended_vector_splits_and_classifier_parity(self):
        from nids.inference import Predictor
        root=Path(__file__).resolve().parents[1]
        manifest=pd.read_csv(root/'data/extended/processed/split_manifest.csv')
        hashes=[set(manifest.loc[manifest.split==s,'feature_hash']) for s in ['train','validation','test']]
        self.assertFalse(hashes[0]&hashes[1]);self.assertFalse(hashes[0]&hashes[2]);self.assertFalse(hashes[1]&hashes[2])
        pred=Predictor(root/'artifacts/extended').predict(pd.read_csv(root/'data/extended/processed/test_flows.csv'))
        saved=pd.read_csv(root/'results/extended/Transformer_test_predictions.csv')
        self.assertEqual(pred.predicted_class.tolist(),saved.predicted_class.tolist())
        self.assertIn('atypical_flag',pred)

if __name__=='__main__':unittest.main()
