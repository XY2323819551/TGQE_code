import json
import os
import argparse


def generate_expanded_query(path_topics, data_name, path_pred, path_out, settings, n_pred, topk_em):
    with open(path_topics, "r", encoding="utf-8") as f2:
        orig_queries = f2.readlines()
    with open(path_pred, "r", encoding="utf-8") as f:
        new_queries = []
        data_pred = json.load(f)
        for k, (query, preds) in enumerate(data_pred.items()):
            preds = preds[settings][str(topk_em)]
            if len(preds) < n_pred:
                for i in range(len(preds)):
                    query = query + " " + preds[i]
            else:
                for i in range(n_pred):
                    query = query + " " + preds[i]
            new_queries.append(query + "\t" + orig_queries[k].strip().split("\t")[1] + "\n")
    with open(path_out + os.path.sep + data_name + ".garfusion." + str(topk_em) + ".hybrid-npred" + str(n_pred) + ".csv", "w", encoding="utf-8") as f2:
        f2.writelines(new_queries)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some parameters.')
    parser.add_argument('--path-topics', type=str, default=None, help='path to initial test queries')
    parser.add_argument('--data-name', type=str, default=None, help='nq-test or trivia-test')
    parser.add_argument('--path-pred', type=str, default=None, help='path to reader results')
    parser.add_argument('--path-out', type=str, default=None, help='path to save the expanded query')
    parser.add_argument('--settings', type=str, default=None, help='the value of beta and gamma, fusion strategy')
    parser.add_argument('--n-pred', type=int, default=1)
    parser.add_argument('--topk-em', type=int, default=500, help='the number of passage to reader')
    args = parser.parse_args()

    generate_expanded_query(args.path_topics, args.data_name, args.path_pred, args.path_out, args.settings, args.n_pred, args.topk_em)
    print("Finished!")
