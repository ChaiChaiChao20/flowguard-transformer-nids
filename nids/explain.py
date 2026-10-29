"""Actual SHAP and LIME explanations for the delivered predictor."""
import numpy as np
import pandas as pd
from .schema import FEATURES


def explain_shap(predictor,background,row,samples=128):
    import shap
    values=background[FEATURES].astype(float).to_numpy()
    def predict(x):return predictor.probabilities(pd.DataFrame(x,columns=FEATURES))
    explainer=shap.KernelExplainer(predict,values[:20])
    attribution=explainer.shap_values(row[FEATURES].astype(float).to_numpy(),nsamples=samples,silent=True)
    attribution=np.asarray(attribution)
    cls=int(predict(row)[0].argmax())
    selected=attribution[0,:,cls]
    return pd.DataFrame({'feature':FEATURES,'shap_value':selected}),{
        'predicted_class':predictor.classes[cls],'expected_probability':float(explainer.expected_value[cls]),
        'predicted_probability':float(predict(row)[0,cls]),'attribution_sum':float(selected.sum()),
        'method':'SHAP KernelExplainer','background_rows':min(20,len(values)),'samples':samples}


def explain_lime(predictor,background,row,samples=1000):
    from lime.lime_tabular import LimeTabularExplainer
    train=background[FEATURES].astype(float).to_numpy()
    explainer=LimeTabularExplainer(train,feature_names=FEATURES,class_names=predictor.classes,
                                  mode='classification',random_state=42,discretize_continuous=True)
    def predict(x):return predictor.probabilities(pd.DataFrame(x,columns=FEATURES))
    x=row[FEATURES].iloc[0].to_numpy(dtype=float);cls=int(predict(x[None,:])[0].argmax())
    explanation=explainer.explain_instance(x,predict,labels=[cls],num_features=len(FEATURES),num_samples=samples)
    return pd.DataFrame(explanation.as_list(label=cls),columns=['condition','lime_weight']),{
        'method':'LIME Tabular','predicted_class':predictor.classes[cls],
        'local_surrogate_r2':float(explanation.score),'samples':samples}
