# Text generated-based expansion retrieval (tgqe)

This repo provides the code and resources of TGQE.

## Installation
```
conda create -n TGQE python=3.8
pip install torch==1.8.1+cu111 -f https://download.pytorch.org/whl/torch_stable.html
pip install -r requirements.txt
```

## Data

- Most of our code comes from [Pyserini](https://github.com/XY2323819551/pyserini/blob/master/docs/experiments-dpr.md), [Pygaggle](https://github.com/castorini/pygaggle/blob/master/docs/experiments-dpr-reader.md), [GAR](https://github.com/morningmoni/GAR) and [FID](https://github.com/facebookresearch/FiD). 
- Experiment results are all based on test set of NQ and Trivia, which are open-source.

## Code

### Retrieval

**DPR retrieval** with brute-force index:

```
$ python -m pyserini.dsearch --topics the path to initial query or expanded query \
                             --index wikipedia-dpr-multi-bf \
                             --encoder facebook/dpr-question_encoder-multiset-base \
                             --output runs/file-name.trec \
                             --batch-size 36 --threads 12
```

**BM25 retrieval**

```
$ python -m pyserini.search --topics the path to initial query or expanded query \
                            --index wikipedia-dpr \
                            --output runs/file-name.trec
```

**Hybrid dense-sparse retrieval** 

```
$ python -m pyserini.hsearch dense  --index wikipedia-dpr-multi-bf \
                                    --encoder facebook/dpr-question_encoder-multiset-base \
                             sparse --index wikipedia-dpr \
                             fusion --alpha the value of fusion factor dependes on dataset \
                             run    --topics the path to initial query or expanded query \
                                    --batch-size 36 --threads 12 \
                                    --output runs/file-name.trec 
```

`--topics`: Path to queries, you can choose initial query or expanded query of NQ and Trivia.

`--index`: If you download them, you can replace them with local paths, which may be faster.

`--output`: Path to save your retrieval results.

`--fusion`: In first cycle, we set fusion factor to $1.3$ and $0.95$ for NQ and Trivia respectively. And for second cycle, we set $1.0$ and $0.95$ for both dataset respectively.



To evaluate, first convert the TREC output format to DPR's `json` format:

```
$ python -m pyserini.eval.convert_trec_run_to_dpr_retrieval_run --topics the path to initial query or expanded query \
                                                                --index wikipedia-dpr \
                                                                --input runs/file-name.trec \
                                                                --output runs/file-name.json \
                                                                --store-raw

$ python -m pyserini.eval.evaluate_dpr_retrieval --retrieval runs/file-name.json --topk 5 20 100 500 1000
```



### Extractive Reader

```
cd 
```



```
$ python -m extractive_reader.evaluate_passage_reader --task wikipedia --retriever score --reader dpr \
                                                  --settings garfusion_beta_gamma \
                                                  --model-name only for Trivia
                                                  --retrieval-file path to save retrieval results \
                                                  --output-file Path to the results of reader inference \
                                                  --topk-em 10 20 50 100 200 500 \
                                                  --device cuda 
```

`--settings`: For sparse retrieval results, we set `garfusion_0.46_0.308` for NQ and `garfusion_0.78_0.093` for Trivia respectively. For hybrid retrieval results, we set `garfusion_0.32_0.1952` for NQ and `garfusion_0.76_0.152` for Trivia respectively.

`--model-name`: For NQ, we set  `--model-name` as `facebook/dpr-reader-single-nq-base`. For Trivia, we set `--model-name` as `facebook/dpr-reader-multiset-base`.

`--retrieval-file`: The input file of reader.

`--output-file`: Path to save the results of reader inference.

`--topk-em`: How many passage selected as the reader input.

`--device`:  cuda or cuda:1, cuda:2...
The above is the operation of the extractive reader. For the operation of the generator reader, see `generative_reader` folder.



### Generating Expanded Query

```
$ python -m scripts.generate_expanded_query --path-topics Path to initial query \
                                            --data-name nq-test or Trivia-tes
                                            --path-pred Path to the results of reader inference \
                                            --path-out Path to save the expanded query \ 
                                            --settings "GAR Fusion, beta=xx, gamma=xx" \
                                            --n-pred Number of reader predictions used as expansion terms \
                                            --topk-em the reader predictions are obtained based on top-k passages
```

`--settings`: For sparse retrieval results, we set `"GAR Fusion, beta=0.46, gamma=0.308"` for NQ and `"GAR Fusion, beta=0.78, gamma=0.093"` for Trivia respectively. For hybrid retrieval results, we set `"GAR Fusion, beta=0.32, gamma=0.1952"` for NQ and `"GAR Fusion, beta=0.76, gamma=0.152"` for Trivia respectively.

### Manual hybrid

Combining the new sparse search results with the original dense search results manually. 

```
$ python -m scripts.manual_hybrid --path-sparse Path to new sparse retrieval results based on expanded query \
                                  --path-dense Path to initial dense retrieval results based on initial query \
                                  --path-topics XX Path to initial query file\
                                  --path-out Path to save the new hybrid retrieval results \
                                  --alpha 1.0 for NQ and 0.95 for Trivia
```

### Reranking

Reranking the initial retrieval results by using new reader predictions based on new retrieval results as reranking signals.

```
$ python -m reranking.rerank --path-data Path to initial retrieval results which needs to rerank \
                             --path-pred Path to the new results of reader inference based on new retrieval results \
                             --path-out Path to save reranking results \
                             --fusion "GAR Fusion, beta=xx, gamma=xx" \
                             --n-contexts sort the first n passage \
                             --topk-em the reader predictions are obtained based on top-k passages \
                             --n-pred Number of reader predictions used as reranking signals
```

`--fusion`: Same as `--setting` above, depends on which kind of retrieval results and dataset we used.

`--topk-em`: Same as `--topk-em` above, but here the top-k passages are selected from the new retrieval results.

### Example

We provide an example based on the NQ dataset that shows how to use these commands. We have written these commands in `command.md`.
