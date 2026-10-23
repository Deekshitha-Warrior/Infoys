"""Accuracy-focused LR experiment. Never replaces the deployed model.

Run from backend: python -m ml.tune_logistic
Uses the existing frozen split; selects exclusively on training CV accuracy.
The test set has been evaluated previously and is not a new external benchmark.
"""
import json
from datetime import datetime, timezone
import numpy as np
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from app.intelligence import ROOT, ARTIFACTS
from ml.features import normalized
from ml.train import metrics


def main():
    records = json.loads((ROOT / 'data/career_profiles.json').read_text(encoding='utf-8'))
    split = json.loads((ARTIFACTS / 'split.json').read_text(encoding='utf-8'))
    train, test = split['train'], split['test']
    if set(train) & set(test) or sorted(train + test) != list(range(len(records))):
        raise ValueError('Frozen split must cover all rows without overlap.')
    texts = np.array([normalized(row['text']) for row in records])
    labels = LabelEncoder().fit_transform([row['career'] for row in records])
    pipeline = Pipeline([
        ('features', FeatureUnion([
            ('word', TfidfVectorizer(sublinear_tf=True)),
            ('char', TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=2, sublinear_tf=True)),
        ])),
        ('classifier', LogisticRegression(max_iter=2000, random_state=42)),
    ])
    grid = {
        'features__word__ngram_range': [(1, 1), (1, 2)],
        'features__transformer_weights': [{'word': 1, 'char': 0}, {'word': 1, 'char': 1}, {'word': 0, 'char': 1}],
        'classifier__C': [0.1, 1, 10, 100],
        'classifier__class_weight': [None, 'balanced'],
    }
    search = GridSearchCV(pipeline, grid, scoring={'accuracy': 'accuracy', 'f1_macro': 'f1_macro'},
        refit='accuracy', cv=StratifiedKFold(5, shuffle=True, random_state=42), n_jobs=2)
    search.fit(texts[train], labels[train])
    result = {
        'evaluated_at': datetime.now(timezone.utc).isoformat(),
        'train_rows': len(train), 'test_rows': len(test),
        'candidate_count': len(search.cv_results_['params']),
        'selection': 'Five-fold training-only CV accuracy; frozen seed-42 test split unchanged.',
        'best_cv_accuracy': float(search.best_score_),
        'best_parameters': search.best_params_,
        'test': metrics(labels[test], search.predict_proba(texts[test])),
        'target_accuracy': 0.65,
        'deployed': False,
        'limitations': ['Previously evaluated small survey holdout; not independent external validation.',
            'No labels changed, no synthetic rows, no test rows used during fitting or CV selection.',
            'Existing production model retained; this experiment does not automatically promote models.'],
    }
    result['target_met'] = result['test']['accuracy'] >= result['target_accuracy']
    (ARTIFACTS / 'logistic_accuracy_experiment.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
