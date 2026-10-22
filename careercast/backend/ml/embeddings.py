"""Fine-tune a sentence encoder on O*NET occupational descriptions and skills."""

import csv
import json
import random
from functools import lru_cache
from app.intelligence import ROOT, ARTIFACTS, ALIASES, CAREERS

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
MODEL_DIR = ARTIFACTS / "sentence_encoder"
EVALUATION_PAIRS = [
    ("JavaScript", "JS"),
    ("Python", "Python programming"),
    ("PostgreSQL", "Postgres"),
    ("Amazon Web Services", "AWS"),
    ("Kubernetes", "K8s"),
    ("React", "React.js"),
    ("Machine learning", "ML"),
    ("Google Cloud Platform", "GCP"),
    ("Microsoft Excel", "Excel spreadsheet"),
    ("SQL", "Structured Query Language"),
]


@lru_cache(maxsize=1)
def encoder():
    from sentence_transformers import SentenceTransformer
    import torch

    torch.set_num_threads(4)
    return SentenceTransformer(str(MODEL_DIR), device="cpu")


@lru_cache(maxsize=3000)
def encode_one(text):
    return encoder().encode([text], normalize_embeddings=True, show_progress_bar=False)[
        0
    ]


def main():
    import torch
    import numpy as np
    from torch.utils.data import DataLoader
    from sentence_transformers import SentenceTransformer, InputExample, losses

    torch.set_num_threads(4)
    torch.manual_seed(42)
    rng = random.Random(42)
    occupations = list(
        csv.DictReader((ROOT / "data/onet_occupations.csv").open(encoding="utf-8-sig"))
    )
    software = {}
    for row in csv.DictReader(
        (ROOT / "data/onet_software_skills.csv").open(encoding="utf-8-sig")
    ):
        software.setdefault(row["O*NET-SOC Code"], []).append(row["Workplace Example"])
    # Select occupations deterministically; no survey validation records enter fine-tuning.
    occupations = [r for r in occupations if r["O*NET-SOC Code"] in software]
    rng.shuffle(occupations)
    training = occupations[:240]
    examples = []
    for index, row in enumerate(training):
        description = row["Description"]
        skill_text = ", ".join(sorted(set(software[row["O*NET-SOC Code"]]))[:20])
        examples.append(
            InputExample(
                texts=[description, f'{row["Title"]}. Relevant software: {skill_text}'],
                label=1.0,
            )
        )
        negative = training[(index + 73) % len(training)]
        examples.append(
            InputExample(texts=[description, negative["Description"]], label=0.0)
        )
    model = SentenceTransformer(MODEL_ID, revision=MODEL_REVISION, device="cpu")
    model.max_seq_length = 128
    # Explicit loop avoids optional Trainer/datasets integrations; optimizes encoder weights.
    loss_fn = losses.CosineSimilarityLoss(model)
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
    loader = DataLoader(
        examples, shuffle=True, batch_size=16, collate_fn=model.smart_batching_collate
    )
    model.train()
    for step, (features, labels) in enumerate(loader):
        optimizer.zero_grad()
        loss = loss_fn(features, labels)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        if step % 10 == 0:
            print(
                f"Embedding fine-tuning step {step}/{len(loader)} loss={loss.item():.4f}",
                flush=True,
            )
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model.save(str(MODEL_DIR))
    model.eval()
    # Store compact skill vectors so API inference needs no model download or torch.
    skill_names = sorted(set(s for values in CAREERS.values() for s in values))
    skill_vectors = model.encode(
        skill_names, normalize_embeddings=True, show_progress_bar=False
    )
    (ARTIFACTS / "skill_embeddings.json").write_text(
        json.dumps(
            {
                "model": MODEL_ID,
                "fine_tuned": True,
                "vectors": dict(zip(skill_names, skill_vectors.tolist())),
            }
        ),
        encoding="utf-8",
    )
    left = model.encode([a for a, b in EVALUATION_PAIRS], normalize_embeddings=True)
    right = model.encode([b for a, b in EVALUATION_PAIRS], normalize_embeddings=True)
    similarities = np.sum(left * right, axis=1)
    result = {
        "base_model": MODEL_ID,
        "fine_tuning": "One epoch of cosine-similarity training on 240 O*NET descriptions, associated software lists, and deterministic mismatched-description negatives. Not fine-tuned on the survey test set.",
        "training_pairs": len(examples),
        "test_pairs": [
            {"left": a, "right": b, "cosine": round(float(s), 4)}
            for (a, b), s in zip(EVALUATION_PAIRS, similarities)
        ],
        "mean_synonym_cosine": round(float(similarities.mean()), 4),
        "fraction_at_least_85": round(float((similarities >= 0.85).mean()), 4),
        "mean_cosine_85_gate": bool(similarities.mean() >= 0.85),
        "limitations": [
            "Small manually curated synonym test; not a SemEval evaluation.",
            "O*NET job descriptions and software associations are weak supervision, not human-annotated synonym pairs.",
        ],
    }
    (ARTIFACTS / "embedding_evaluation.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
