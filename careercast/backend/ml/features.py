"""Shared feature transformer fitted inside each cross-validation fold."""

import re
import json
import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from app.intelligence import CAREERS, ALIASES, ARTIFACTS


def normalized(text):
    text = text.lower()
    for alias, target in sorted(ALIASES.items(), key=lambda item: -len(item[0])):
        text = re.sub(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", target, text)
    return text


class SkillFeatures(BaseEstimator, TransformerMixin):
    def __init__(self, semantic=False):
        self.semantic = semantic

    def fit(self, texts, y=None):
        self.vectorizer_ = TfidfVectorizer(
            ngram_range=(1, 2), max_features=2500, sublinear_tf=True
        )
        self.vectorizer_.fit([normalized(t) for t in texts])
        self.skill_names_ = sorted(
            set(s for values in CAREERS.values() for s in values)
        )
        if self.semantic:
            table = json.loads(
                (ARTIFACTS / "skill_embeddings.json").read_text(encoding="utf-8")
            )["vectors"]
            self.embedding_matrix_ = np.array([table[s] for s in self.skill_names_])
        return self

    @property
    def vocabulary_(self):
        return self.vectorizer_.vocabulary_

    def transform(self, texts):
        cleaned = [normalized(text) for text in texts]
        binary = [
            [
                float(bool(re.search(r"(?<!\w)" + re.escape(skill) + r"(?!\w)", text)))
                for skill in self.skill_names_
            ]
            for text in cleaned
        ]
        blocks = [self.vectorizer_.transform(cleaned), csr_matrix(binary)]
        if self.semantic:
            multi = np.array(binary)
            averaged = (
                multi
                @ self.embedding_matrix_
                / np.maximum(multi.sum(axis=1, keepdims=True), 1)
            )
            norms = np.linalg.norm(averaged, axis=1, keepdims=True)
            averaged = averaged / np.maximum(norms, 1e-9)
            blocks.append(csr_matrix(averaged))
        return hstack(blocks).tocsr()
