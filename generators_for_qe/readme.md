



### Introduction

Query expansion is a widely-used technique for improving retrieval efficiency in pipeline-based open-domain question answering (OpenQA) systems. By increasing lexical overlap and topic relevance between queries and relevance passages, it improves performance in subsequent stages. The key lies in selecting appropriate query expansion terms. This paper introduces Hybrid Text Generation-Based Query Expansion (HTGQE), an effective method to improve retrieval efficiency. HTGQE combines large language models with pseudo-relevance feedback techniques to enhance the input for generative models, which improves the speed and quality of text generation. Building on this foundation, HTGQE employs multiple query expansion generators, each trained to provide query expansion contexts from distinct perspectives. This enables the retriever to explore relevant passages from various angles for complementary retrieval results. As a result, the retriever can more efficiently and effectively obtain relevant passages. As a result, under an extractive and generative QA setup, TGQE achieves promising results on both Natural Questions (NQ) and TriviaQA (Trivia) datasets for passage retrieval and reading tasks.

<img src="/Users/zhangxiaoyu/Desktop/workspace/CODE_New/mdpi/论文/images&tables/framework_TGQE.jpeg" alt="framework_TGQE" style="zoom:30%;" />



### Preparation

- The installation of the conda environment can also refer to [Generative Reader]([QCER_GenerateReader](https://github.com/XY2323819551/QCER_GenerateReader)) or [FiD](https://github.com/facebookresearch/FiD).
- It is necessary to prepare an R2 system, including a retriever and a reader.
   - 🚀 The operation steps and data resource of the retrieval phase [here.](https://github.com/XY2323819551/QCER_for_OpenQA)
   - 🚀 The operation steps and data resource of the extractive reader [here.](https://github.com/XY2323819551/QCER_for_OpenQA)
   - 🚀 Operational steps and data resource of Generative Reader [here](https://github.com/XY2323819551/QCER_GenerateReader).

- Train three different query expansion generators.
  - ***ctx*(*A*):** Using the answer as query expansion term is valuable for retrieving passages containing the target. 
  - ***ctx*(*S*):** Sentence containing the default target. 
  - ***ctx*(*T*):** Title of the target passage. Titles of relevant passages frequently represent notable entities and occasionally provide answers to queries.
  - 🚀 The training data for three query expansion generators are[这里](https://pan.baidu.com/s/1Q9ifMayvHJm62mJ04OSNrg?pwd=6666 ).

### Code

In the paper, BART-large is employed as the query expansion generator, with the generative model training conducted on two Tesla V100 GPUs. For both the NQ and Trivia, the learning rate can be uniformly set at 3e-5; however, when training the G_T , it is advisable  to increase the learning rate, such as by adjusting it to 1e-4. While training the *G_A*, *G_S* and *G_T*, the batch sizes are set at 64, 16, and 8, respectively; for the Trivia dataset, they are 16, 8 and 8. Furthermore, due to the incorporation of PRF, the maximum input length is set to 768 tokens, with the maximum generation lengths being 16 (*ctx*(*A*)), 64 (*ctx*(*S*)), and 32 (*ctx*(*T*)) tokens, respectively.

**Training Command**

```
GEN_TARGET='XXX' python train_generator.py --remark xxx --train_batch_size xxx --eval_batch_size xxx --ckpt_metric val-ROUGE-1
```

- GEN_TARGET: According to the training type, select from "answer", "sentence" or "title".
- remark: Mark the current training process, and the name can be distinguished from other processes.

**Inference Command**

```
python test_generator.py --input_path $$DATA_DIR/test.source --output_path $$DATA_DIR/output.txt --bs 32 --model_ckpt checkpoint.ckpt --max_source_length 1024 --max_target_length 10 --remark generator_train_nq_A
```

- input_path：Path to the test dataset.
- output_path：The output path of the test dataset results.
- model_ckpt：Model path

### Scripts

The script for fusing three types of retrieval results is `merge_data.py`.









