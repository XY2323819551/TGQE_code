import json
from tqdm import trange
from retrieval.pyserini.eval.evaluate_dpr_retrieval import has_answers, SimpleTokenizer
import argparse

parser = argparse.ArgumentParser(description='Process some parameters.')
parser.add_argument('--path-sparse', type=str, default=None, help='path to new sparse retrieval results')
parser.add_argument('--path-dense', type=str, default=None, help='path to dense retrieval results')
parser.add_argument('--path-topics', type=str, default=None, help='path to initial test queries')
parser.add_argument('--path-out', type=str, default=None, help='path to save hybrid results')
parser.add_argument('--alpha', type=float, default=1.0)
parser.add_argument('--top-k', type=int, default=1000)
args = parser.parse_args()

tokenizer = SimpleTokenizer()


def hybrid(dense_result, sparse_result, alpha, k):
    dense_hits = {hit["docid"]: [hit["score"], hit["has_answer"], hit["title"], hit["text"]] for hit in
                  dense_result["contexts"]}
    sparse_hits = {hit["docid"]: [hit["score"], hit["has_answer"], hit["title"], hit["text"]] for hit in
                   sparse_result["contexts"]}
    hybrid_result = []
    dense_hits_values_score = [float(value[0]) for value in dense_hits.values()]
    sparse_hits_values_score = [float(value[0]) for value in sparse_hits.values()]
    min_dense_score = min(dense_hits_values_score) if len(dense_hits) > 0 else 0
    min_sparse_score = min(sparse_hits_values_score) if len(sparse_hits) > 0 else 0
    for doc in set(dense_hits.keys()) | set(sparse_hits.keys()):
        if doc not in dense_hits:
            tmp_value = [value for value in sparse_hits[doc]]
            score = alpha * float(tmp_value[0]) + min_dense_score
            has_answer, title, text = "", tmp_value[2], tmp_value[3]
        elif doc not in sparse_hits:
            tmp_value = [value for value in dense_hits[doc]]
            score = alpha * min_sparse_score + float(tmp_value[0])
            has_answer, title, text = "", tmp_value[2], tmp_value[3]
        else:
            tmp_value_sparse = [value for value in sparse_hits[doc]]
            tmp_value_dense = [value for value in dense_hits[doc]]
            score_sparse = float(tmp_value_sparse[0])
            score_dense = float(tmp_value_dense[0])
            score = alpha * score_sparse + score_dense
            has_answer, title, text = "", tmp_value_dense[2], tmp_value_dense[3]
        hybrid_result.append({"docid": doc, "score": score, "title": title, "text": text, "has_answer": has_answer})
    hybrid_result = sorted(hybrid_result, key=lambda x: x["score"], reverse=True)[:k]
    for item in hybrid_result:
        item["score"] = str(item["score"])
    return hybrid_result


def add_has_answer(hybrid_result, ans):
    answers = ans.strip().split("\t")[1]
    if answers[0] == '"':
        answers = answers[1:-1].replace('""', '"')
    answers = eval(answers)

    for item in hybrid_result:
        answer_exist = has_answers(item["text"], answers, tokenizer)
        item["has_answer"] = answer_exist


def main():
    with open(args.path_sparse, "r") as f1, open(args.path_dense, "r") as f2, open(args.path_topics, "r") as f3:
        sparse_results = json.load(f1)
        dense_results = json.load(f2)
        answers = f3.readlines()

    hybrid_results = {}
    alpha = args.alpha
    k = args.top_k
    for i in trange(len(answers)):
        sparse_result = sparse_results[str(i)]
        dense_result = dense_results[str(i)]
        hybrid_result = hybrid(dense_result, sparse_result, alpha, k)
        add_has_answer(hybrid_result, answers[i])
        sub_dict = {}
        sub_dict["question"] = dense_result["question"]
        sub_dict["answers"] = dense_result["answers"]
        sub_dict["contexts"] = hybrid_result
        hybrid_results[str(i)] = sub_dict

    with open(args.path_out, "w", encoding="utf-8") as f:
        json.dump(hybrid_results, f, indent=4)


if __name__ == "__main__":
    main()
    print("Finished!")
