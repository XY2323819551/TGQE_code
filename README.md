# TGQE_code

⚠️⚠️ We wrote the readme file separately under each folder.

### Introduction

Query expansion is a widely-used technique for improving retrieval efficiency in pipeline-based open-domain question answering (OpenQA) systems. By increasing lexical overlap and topic relevance between queries and relevance passages, it improves performance in subsequent stages. The key lies in selecting appropriate query expansion terms. This paper introduces Hybrid Text Generation-Based Query Expansion (HTGQE), an effective method to improve retrieval efficiency. HTGQE combines large language models with pseudo-relevance feedback techniques to enhance the input for generative models, which improves the speed and quality of text generation. Building on this foundation, HTGQE employs multiple query expansion generators, each trained to provide query expansion contexts from distinct perspectives. This enables the retriever to explore relevant passages from various angles for complementary retrieval results. As a result, the retriever can more efficiently and effectively obtain relevant passages. As a result, under an extractive and generative QA setup, TGQE achieves promising results on both Natural Questions (NQ) and TriviaQA (Trivia) datasets for passage retrieval and reading tasks.


### Preparation

- The installation of the conda environment can also refer to [Generative Reader]([QCER_GenerateReader](https://github.com/XY2323819551/QCER_GenerateReader)) or [FiD](https://github.com/facebookresearch/FiD).
- It is necessary to prepare an R2 system, including a retriever and a reader.
  - 🚀 The operation steps and data resource of the retrieval phase [here.](https://github.com/XY2323819551/QCER_for_OpenQA)
  - 🚀 The operation steps and data resource of the extractive reader [here.](https://github.com/XY2323819551/QCER_for_OpenQA)
  - 🚀 Operational steps and data resource of Generative Reader [here](https://github.com/XY2323819551/QCER_GenerateReader).

- Train three different query expansion generators.
  - ctx(A): Using the answer as query expansion term is valuable for retrieving passages containing the target. 
  - ctx(S): Sentence containing the default target. 
  - ctx(T): Title of the target passage. Titles of relevant passages frequently represent notable entities and occasionally provide answers to queries.
  - 🚀 The training data for three query expansion generators are[这里](https://pan.baidu.com/s/1Q9ifMayvHJm62mJ04OSNrg?pwd=6666 ).
