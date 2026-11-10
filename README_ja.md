# KCI-Vec

**アプリに組み込む、暗号化できるベクトル検索。**
プロセスの中で動く 1 つのライブラリ。サーバも依存もなく、ノート PC から Xeon まで動きます。

*[English](README.md)* · **紹介ページ:** <https://claude.ai/artifact/CCvYMLaDGKzNeFKUBGR69A#ja>

このリポジトリでは **評価用の部品** を配っています。Linux x86-64 用の Python の wheel で、cosine 類似度に対応しています。

---

## ひと目で

| | |
|---|---|
| **組み込み** | アプリのプロセスの中で動きます。サーバも JVM も、運用の手間もありません |
| **暗号化** | 保存する索引は AES-256-CTR で暗号化し、AES-256-CMAC で改ざんを検出します。鍵違いや書き換えられたファイルは読み込みません。検索は速いままです |
| **軽い** | 1 次元 1 バイト。float32 の約 4 分の 1 のメモリで動きます |
| **速い** | 公式 ANN-Benchmarks の手順で ScaNN 1.4.2 の約 2〜5 倍。qsgngt とも、同じ機械で並ぶか上回ります |
| **更新できる** | 作ったあとも追加・削除・詰め直しができます。属性での絞り込み、キーワードとベクトルを合わせた検索にも対応 |

想定しているのは、**データを外に出せない検索**です。手元の端末やデスクトップのアプリ、規制のある業界の社内システム、
利用者ごとに分けたサービス。そして、検索のためだけにベクトル DB を運用したくない場合です。

---

## 速さ

glove-100-angular (118 万件 × 100 次元)、公式 ANN-Benchmarks の手順 (k=10、1 コア、質問 1 万、各設定 5 回の最速)。
recall@10 が 0.90 / 0.95 / 0.99 以上での最良 QPS (1 秒あたりの検索数) です。

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/img/glove100_qps_ja_dark.svg">
  <img alt="glove-100-angular の recall@10 0.90 / 0.95 / 0.99 での最良 QPS。Xeon 8375C と Ryzen 9 9950X で、KCI-Vec グラフ方式・区分け方式・qsgngt・ScaNN・hnswlib を並べた棒グラフ。値は下の表。" src="docs/img/glove100_qps_ja_light.svg" width="960">
</picture>

| 算法 | Intel Xeon 8375C (AWS r6id.4xlarge) | AMD Ryzen 9 9950X |
|---|---|---|
| **KCI-Vec グラフ方式** (詰めた配置、先行版) | **16,253 / 9,851 / 4,414** | **36,951 / 21,800 / 9,440** |
| **KCI-Vec 区分け方式** | 12,331〜14,725 / 8,694〜10,493 / 3,302〜4,138 | 34,670 / 24,321 / 9,747 |
| qsgngt 5.0.0 (公式の全設定) | 16,339〜16,809 / 10,282〜10,618 / 3,408〜3,789 | 27,678 / 15,089 / 6,099 |
| ScaNN 1.4.2 (公式の全設定) | 4,438〜4,508 / 2,190〜2,219 / 783〜794 | 15,611 / 8,195 / 3,085 |
| hnswlib 0.8.0 | — | 4,268 / 1,898 / 685 |

- 幅のある値は、同じ機械で繰り返した計測の最小〜最大です。KCI-Vec 区分け方式と ScaNN は 6 回、qsgngt は 3 回、それ以外は 1 回です。
- **すべて開発者自身の計測で、第三者による確認はまだありません。** ann-benchmarks.com の数字とは比べていません (時期も機械も違うため)。
- 順位は CPU と目標の recall で変わります。一般的な順位ではなく、特定の条件での計測としてご覧ください。

---

## 2 つの探し方

- **グラフ方式** — 近いベクトルどうしを線でつなぎ、質問に近いほうへたどります。追加・削除に対応し、詰めた配置 (先行版) で上の表の最上段の数字が出ます。
- **区分け方式** — ベクトルをかたまりに分け、質問に近いかたまりだけを調べます。グラフを作る必要がありません。

どちらも暗号化保存、属性での絞り込み、float での並べ直しに対応しています。

---

## 入れ方

```sh
pip install https://github.com/KimYuki3/kci-vec-dist/releases/download/v0.1.1/kci_vec-0.1.1-py3-none-manylinux_2_35_x86_64.whl
```

必要なもの: Linux x86-64 (glibc 2.35 以降。例えば Ubuntu 22.04 以降、Debian 12 以降)、AVX2 のある CPU (AVX-512 があれば使います)、
Python 3.8 以降、NumPy。

wheel の sha256: `8041d142e2e6a7f468583dbf389b877e58ffacf580ab104cdf51ec2110e2920b`

---

## 使い方

```python
import numpy as np
from kci_vec import KciVec

v = KciVec(dim=384, rerank=200)            # 並べ直し用に float を残す
v.add_many(range(len(embeddings)), embeddings)
v.build_lists()                            # 区分け方式 (グラフ方式なら v.build())

for doc_id, score in v.search(query, k=10):
    ...

allowed = {3, 17, 42}
hits = v.search(query, k=10, filter=lambda i: i in allowed)   # 属性・権限での絞り込み

v.save("index.kv", key=b"a long secret")   # 暗号化して保存
v2 = KciVec.load("index.kv", key=b"a long secret")
```

点数は cosine 類似度で、高い順に返ります。たくさんの質問をまとめて探すときは、`v.search_many(queries, k=10)` が `(ids, scores)` の配列を返します。

---

## 評価用の部品の制限

- Linux x86-64 のみ、cosine 類似度のみです。
- グラフ方式の詰めた配置は先行版です。まだ保存できず、追加すると作り直すまで外れます。
- 書き込みは 1 本ずつです。探している最中に索引を変えないでください。
- 作る間は float のベクトルをメモリに持ちます。SSD に置いたまま探す索引はまだありません。

---

## ライセンス

研究・教育・個人・その他の非商用の利用は無償です。商用の利用には別の契約が必要です。
詳しくは [LICENSE](LICENSE) をご覧ください。© 2026 Yukihiro Kimura。

**連絡先** — 質問・不具合の報告・商用の契約のご相談は、このリポジトリの Issue へどうぞ
([KimYuki3/kci-vec-dist](https://github.com/KimYuki3/kci-vec-dist/issues))。Issue は公開されます。商用のご相談は一言だけ書いていただければ、
そこから非公開の連絡方法をご案内します。
