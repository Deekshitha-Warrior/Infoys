"""Authenticated HTTP benchmark against a running API; uses a dedicated test account."""
import argparse
import asyncio
import json
import os
import time
from pathlib import Path
import httpx
import numpy as np


async def run(url, token, count, concurrency, career):
    headers = {"Authorization": "Bearer " + token}
    timings, errors = [], []
    async with httpx.AsyncClient(base_url=url, headers=headers, timeout=60) as client:
        endpoints = ["/api/intelligence/recommend", "/api/intelligence/gap-report", "/api/intelligence/predict"]
        for path in endpoints:
            response = await client.request("POST" if path.endswith("predict") else "GET", path, params={"career": career} if path.endswith("gap-report") else {})
            response.raise_for_status()
        semaphore = asyncio.Semaphore(concurrency)
        async def one(i):
            async with semaphore:
                start = time.perf_counter()
                path = endpoints[i % 3]
                try:
                    response = await client.request("POST" if path.endswith("predict") else "GET", path, params={"career": career} if path.endswith("gap-report") else {})
                    response.raise_for_status()
                    timings.append((path, (time.perf_counter() - start) * 1000))
                except httpx.HTTPError:
                    errors.append(path)
        await asyncio.gather(*(one(i) for i in range(count)))
    per_endpoint = {}
    for path in {p for p, _ in timings}:
        values = [ms for p, ms in timings if p == path]
        per_endpoint[path] = {"requests": len(values), "p50_ms": round(float(np.percentile(values, 50)), 2), "p95_ms": round(float(np.percentile(values, 95)), 2)}
    return {"requests": count, "concurrency": concurrency, "errors": len(errors), "endpoints": per_endpoint,
        "target_p95_ms": 300, "passed": not errors and len(per_endpoint) == 3 and all(r["p95_ms"] <= 300 for r in per_endpoint.values()),
        "scope": "Warm-model local HTTP prediction, recommendation and gap queries including authentication, database reads and prediction-history writes. Excludes cold starts and hosted-network guarantees."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--career", default="Software Developer")
    parser.add_argument("--output", default="../artifacts/api_benchmark.json")
    args = parser.parse_args()
    if args.requests < 3 or args.concurrency < 1:
        parser.error("Use at least 3 requests and positive concurrency")
    token = os.getenv("CAREERCAST_BENCHMARK_TOKEN")
    if not token:
        parser.error("Set CAREERCAST_BENCHMARK_TOKEN to your own test account token in the environment")
    result = asyncio.run(run(args.url, token, args.requests, args.concurrency, args.career))
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
