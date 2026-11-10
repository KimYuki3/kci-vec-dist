# KCI-Vec

**Embedded vector search, encrypted at rest.**
One in-process library — no server, no dependencies — from a laptop to a Xeon.

*[日本語](README_ja.md)* · **Overview page:** <https://claude.ai/artifact/CCvYMLaDGKzNeFKUBGR69A>

This repository hosts the **evaluation build**: a Python wheel for Linux x86-64, cosine similarity.

---

## At a glance

| | |
|---|---|
| **Embedded** | Runs inside your process. No server, no JVM, nothing to operate |
| **Encrypted at rest** | Saved indexes are encrypted (AES-256-CTR) and authenticated (AES-256-CMAC). Wrong keys and tampered files are refused. Search runs at full speed |
| **Compact** | One byte per dimension — about a quarter of float32 |
| **Fast** | On the official ANN-Benchmarks harness, roughly 2–5× ScaNN 1.4.2, and on par with or ahead of qsgngt on the same machines |
| **Updatable** | Insert, delete and compact after the build. Metadata filtering. Hybrid keyword + vector ranking |

Built for search over data that must not leave the machine: on-device and desktop apps, in-house systems in regulated
industries, single-tenant services — and anyone who would rather not run a vector database just to search.

---

## Speed

glove-100-angular (1.18 M × 100), official ANN-Benchmarks harness: k = 10, one CPU core, 10,000 queries, best of 5 runs
per setting. Best QPS at recall@10 ≥ 0.90 / 0.95 / 0.99.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/img/glove100_qps_en_dark.svg">
  <img alt="Best QPS at recall@10 0.90 / 0.95 / 0.99 on glove-100-angular, Xeon 8375C and Ryzen 9 9950X: KCI-Vec graph, KCI-Vec partitioned, qsgngt, ScaNN, hnswlib. Values in the table below." src="docs/img/glove100_qps_en_light.svg" width="960">
</picture>

| algorithm | Intel Xeon 8375C (AWS r6id.4xlarge) | AMD Ryzen 9 9950X |
|---|---|---|
| **KCI-Vec — graph** (compact layout, preview) | **16,253 / 9,851 / 4,414** | **36,951 / 21,800 / 9,440** |
| **KCI-Vec — partitioned** | 12,331–14,725 / 8,694–10,493 / 3,302–4,138 | 34,670 / 24,321 / 9,747 |
| qsgngt 5.0.0 (full official config) | 16,339–16,809 / 10,282–10,618 / 3,408–3,789 | 27,678 / 15,089 / 6,099 |
| ScaNN 1.4.2 (full official config) | 4,438–4,508 / 2,190–2,219 / 783–794 | 15,611 / 8,195 / 3,085 |
| hnswlib 0.8.0 | — | 4,268 / 1,898 / 685 |

- Ranges are min–max over repeated runs on the same machine: six runs for KCI-Vec partitioned and ScaNN, three for qsgngt, one otherwise.
- **All figures are the author's own measurements and have not been independently verified.** They are not compared
  with the figures on ann-benchmarks.com, which were taken at another time on other machines.
- Rankings depend on the CPU and the recall target; treat these as specific measurements, not a general ranking.

---

## Two index types

- **Graph** — links each vector to its nearest neighbours and walks towards the query. Takes inserts and deletes; the
  compact layout (preview) gives the top figures above.
- **Partitioned** — groups the vectors and scans only the groups nearest to the query. No graph to build.

Both support encrypted save / load, metadata filtering and float re-ranking.

---

## Install

```sh
pip install https://github.com/KimYuki3/kci-vec-dist/releases/download/v0.1.1/kci_vec-0.1.1-py3-none-manylinux_2_35_x86_64.whl
```

Requirements: Linux x86-64 with glibc 2.35 or later (e.g. Ubuntu 22.04+, Debian 12+), a CPU with AVX2 (AVX-512 is
used when present), Python 3.8+, NumPy.

sha256 of the wheel: `8041d142e2e6a7f468583dbf389b877e58ffacf580ab104cdf51ec2110e2920b`

---

## Quick start

```python
import numpy as np
from kci_vec import KciVec

v = KciVec(dim=384, rerank=200)            # keep the float vectors for re-ranking
v.add_many(range(len(embeddings)), embeddings)
v.build_lists()                            # partitioned index (v.build() for the graph)

for doc_id, score in v.search(query, k=10):
    ...

allowed = {3, 17, 42}
hits = v.search(query, k=10, filter=lambda i: i in allowed)   # metadata / access control

v.save("index.kv", key=b"a long secret")   # encrypted at rest
v2 = KciVec.load("index.kv", key=b"a long secret")
```

Scores are cosine similarities, highest first. For many queries at once, `v.search_many(queries, k=10)` returns
`(ids, scores)` arrays.

---

## Limitations of the evaluation build

- Linux x86-64 only, cosine similarity only.
- The compact graph layout is a preview: it is not saved yet, and an insert drops it until it is rebuilt.
- One writer at a time: do not modify an index while searching it.
- During a build the float vectors are held in memory; an SSD-resident index is not available.

---

## License

Free for research, educational, personal and other non-commercial use; commercial use requires a separate license.
See [LICENSE](LICENSE). © 2026 Yukihiro Kimura.

**Contact** — questions, bug reports and commercial licensing: open an issue in this repository
([KimYuki3/kci-vec-dist](https://github.com/KimYuki3/kci-vec-dist/issues)). Issues are public; for a commercial inquiry,
a one-line issue is enough and a private channel will be arranged from there.
