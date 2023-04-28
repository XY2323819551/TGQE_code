

### Passage retrieval 和Passage reading实验（以NQ数据集为例）

首先进入检索项目目录

```
cd XX/OCER/retrieval
```

开始进行混合检索，并评估结果，得到$R_{Hybrid}$

```
python -m pyserini.hsearch dense --index indexes/dindex-wikipedia-dpr_multi-bf-20200127-f403c3 --encoder facebook/dpr-question_encoder-multiset-base sparse --index indexes/index-wikipedia-dpr-20210120-d1b9e6 fusion --alpha 1.3 run --topics topics/initial_query/nq-test.csv --batch-size 36 --threads 12 --output runs/nq/run.dpr.nq-test.hybrid.trec

python -m pyserini.eval.convert_trec_run_to_dpr_retrieval_run --topics topics/initial_query/nq-test.csv --index indexes/index-wikipedia-dpr-20210120-d1b9e6 --input runs/nq/run.dpr.nq-test.hybrid.trec --output runs/nq/run.dpr.nq-test.hybrid.json --store-raw

python -m pyserini.eval.evaluate_dpr_retrieval --retrieval runs/nq/run.dpr.nq-test.hybrid.json --topk 5 20 100 500 1000
```

返回上级目录

```
cd ..
```

把$R_{Hybrid}$作为reader的输入，进行Reader inference。（note：如果是Trivia数据集，则需要添加`--model-name facebook/dpr-reader-multiset-base`）

```
python -m reading.evaluate_passage_reader --task wikipedia --retriever score --reader dpr --settings garfusion_0.32_0.1952 --retrieval-file retrieval/runs/nq/run.dpr.nq-test.hybrid.json --output-file reading/runs/nq/reader_res_hybrid.json --topk-em 10 20 50 100 200 500 --device cuda:0
```

得到Predicted answers之后，把p=500的情况下的结果的top-1(参数m可以自己设置)answer span添加到原始的query后面。

```
python -m scripts.generate_expanded_query --path-topics retrieval/topics/initial_query/nq-test.csv --data-name nq-test --path-pred reading/runs/nq/reader_res_hybrid.json --path-out retrieval/topics/expanded_query/nq --settings "GAR Fusion, beta=0.32, gamma=0.1952" --n-pred 1 --topk-em 500
```

用新的扩展后的query再次进行sparse retrieval

先进入到retrieval 目录下

```
cd retrieval
```

进行检索，得到$R'_{Sparse}$

```
python -m pyserini.search --topics topics/expanded_query/nq/nq-test.garfusion.500.hybrid-npred1.csv --index indexes/index-wikipedia-dpr-20210120-d1b9e6 --output runs/nq/run.dpr.nq-test.bm25.new.trec

python -m pyserini.eval.convert_trec_run_to_dpr_retrieval_run --topics topics/expanded_query/nq/nq-test.garfusion.500.hybrid-npred1.csv --index indexes/index-wikipedia-dpr-20210120-d1b9e6 --input runs/nq/run.dpr.nq-test.bm25.new.trec --output runs/nq/run.dpr.nq-test.bm25.new.json --store-raw
```

为了得到$R'_{Hybrid}$，是$R'_{Sparse}$和初始$R_{Dense}$的结合，还需要进行Dense retrieval.

（如果没有dense retrieval results，就检索）

```
python -m pyserini.dsearch --topics topics/initial_query/nq-test.csv --index indexes/dindex-wikipedia-dpr_multi-bf-20200127-f403c3 --encoder facebook/dpr-question_encoder-multiset-base --output runs/nq/run.dpr.nq-test.multi.bf.trec --batch-size 36 --threads 12

python -m pyserini.eval.convert_trec_run_to_dpr_retrieval_run --topics topics/initial_query/nq-test.csv --index indexes/index-wikipedia-dpr-20210120-d1b9e6 --input runs/nq/run.dpr.nq-test.multi.bf.trec --output runs/nq/run.dpr.nq-test.multi.bf.json --store-raw

python -m scripts.manual_hybrid --path-sparse retrieval/runs/nq/run.dpr.nq-test.bm25.new.json --path-dense retrieval/runs/nq/run.dpr.nq-test.multi.bf.json --path-topics retrieval/topics/initial_query/nq-test.csv --path-out retrieval/runs/nq/manual_hybrid/run.dpr.nq-test.hybrid.new.json --alpha 1.0
```

然后就可以从新的retrieval results（$R'_{Hybrid}$，和$R'_{Sparse}$）选取top-10、top-20....送入Reader进行inference了，得到论文中Passage Reader的结果。

此处的命令以$R'_{Sparse}$为例，要用$R'_{Hybrid}$则可以自己替换命令。

```
cd ..
python -m reading.evaluate_passage_reader --task wikipedia --retriever score --reader dpr --settings garfusion_0.46_0.308 --retrieval-file retrieval/runs/nq/run.dpr.nq-test.bm25.new.json --output-file reading/runs/nq/reader_res_bm25_new.json --topk-em 10 --device cuda:0
```



### Passage reranking实验

如果没有$R_{Sparse}$，先进行原始的sparse retrieval

```
python -m pyserini.search --topics topics/initial_query/nq-test.csv --index indexes/index-wikipedia-dpr-20210120-d1b9e6 --output runs/nq/run.dpr.nq-test.bm25.trec

python -m pyserini.eval.convert_trec_run_to_dpr_retrieval_run --topics topics/initial_query/nq-test.csv --index indexes/index-wikipedia-dpr-20210120-d1b9e6 --input runs/nq/run.dpr.nq-test.bm25.trec --output runs/nq/run.dpr.nq-test.bm25.json --store-raw
```

QCER：上面得到新的$R'_{Sparse}$后，选取top-10 passages送入Reader进行inference，得到预测结果。然后选择1个或者5个预测结果来进行reranking.

```
python -m reranking.rerank --path-data retrieval/runs/nq/run.dpr.nq-test.bm25.json --path-pred reading/runs/nq/reader_res_bm25_new.json --path-out reranking/runs/nq-test.bm25.reranking.QCER.json --fusion "GAR Fusion, beta=0.46, gamma=0.308"
```

然后进行评估。

RIDER：从$R_{Sparse}$中选取top-100 passages送入Reader进行inference，得到预测结果。

```
sparse
python -m reading.evaluate_passage_reader --task wikipedia --retriever score --reader dpr --settings garfusion_0.46_0.308 --retrieval-file retrieval/runs/nq/run.dpr.nq-test.bm25.json --output-file reading/runs/nq/reader_res_bm25.json --topk-em 10 20 50 100 --device cuda:0
```

然后选择1个或者5个预测结果来进行reranking.

```
python -m reranking.rerank --path-data runs/nq/run.dpr.nq-test.bm25.json --path-pred reading/runs/nq/reader_res_bm25.json --path-out reranking/runs/nq-test.bm25.reranking.RIDER.json --fusion "GAR Fusion, beta=0.46, gamma=0.308"
```

