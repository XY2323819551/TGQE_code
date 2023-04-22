"""
重新生成一个文件并保存，包含几个字段：
① init_query；
② expansion_terms；
③ QEvalid(expansion terms是否正确)；
④ answers
⑤ new_query；
⑥ new_retrieval_res（用于选取text内容）

Task1:
这个文件用来辅助挑选四种case:
（1）reader predictions正确，retrieval results含有此答案，NQ/Trivia数据集中比例占多少？(主↑)
（2）reader predictions正确，retrieval results不含此答案，NQ/Trivia数据集中比例占多少？
（3）reader predictions错误，retrieval results含有此答案，NQ/Trivia数据集中比例占多少？
（4）reader predictions错误，retrieval results不含此答案，NQ/Trivia数据集中比例占多少？(主↓)

Task2:
load保存的文件，进行一些结果统计和分析。
比如top-5时NQ上case1+case3的共同提升为24.02，从错误到正确，我要知道case1在这24.02中能占到多少？说明上升是由于case1主导
case2+case4为3.49，从正确到错误，那么case4占到多少比例呢？说明下降主要是由于case4主导的
说明了一点，也就是reader predictions的质量越好，越会往好的方向引导；越坏，则会往越坏的方向引导。

操作方法：
Task1：QEvalid配合ans3即可挑选四种case(ans3指的是new retrieval res中是否有答案；只统计top-5的情况)
Task2：QEvalid配合cases_statistics.py中生成的文件即可
"""

import json
from scripts.utils.tokenizers import SimpleTokenizer
from collections import defaultdict
import unicodedata


def _normalize(text):
    return unicodedata.normalize('NFD', text)


def has_answers(texts, answers, tokenizer):
    texts = _normalize(texts)
    texts = tokenizer.tokenize(texts).words(uncased=True)
    for ans in answers:
        ans = _normalize(ans)
        ans = tokenizer.tokenize(ans).words(uncased=True)
        for text in texts:
            if text in ans:
                return True
    return False


def generate_file(path_topics, path_pred, path_out, settings, topk_em, new_retrieval):
    with open(path_topics, "r", encoding="utf-8") as f2:
        orig_queries = f2.readlines()
    with open(new_retrieval, "r", encoding="utf-8") as f3:
        new_retrieval = json.load(f3)
    with open(path_pred, "r", encoding="utf-8") as f:
        data_pred = json.load(f)
        for k, (_, preds) in enumerate(data_pred.items()):
            query, answers = orig_queries[k].strip().split("\t")
            preds = preds[settings][str(topk_em)]
            new_query = query + " " + preds[0]
            result[str(k)]["init_query"] = query
            result[str(k)]["expansion_terms"] = preds[0]
            result[str(k)]["new_query"] = new_query
            result[str(k)]["new_retrieval_res"] = new_retrieval[str(k)]["contexts"]
            # try:
            #     answers = eval(answers)
            # finally:
            #     print(k)
            result[str(k)]["answers"] = answers
            if has_answers(preds[0], answers, tokenizer):  # 这里需要处理一下
                result[str(k)]["QEvalid"] = 1
            else:
                result[str(k)]["QEvalid"] = 0

    with open(path_out, "w", encoding="utf-8") as f_out:
        json.dump(result, f_out)


if __name__ == "__main__":
    # 生成文件
    data_name = "trivia"  # 或者trivia
    root_path1 = "/home/zhangxy/QA/QCER/retrieval/topics/initial_query/"  # 自行更改
    path_topics = {"nq": "nq-test.csv", "trivia": "trivia-test_processed.csv"}

    root_path2 = "/home/zhangxy/QA/castorini/pygaggle/runs/Reader_res/"  # 自行更改
    preds = {"nq": "1nq-test/reader_res_top10_hybrid.json", "trivia": "2triviaqa-test/reader_res_top10_hybrid.json"}
    # path_pred = root_path2 + preds[0/1]

    root_path3 = "/home/zhangxy/QA/castorini/pyserini/runs/"
    new_retrieval_results = {"nq": "1nq-test/run.dpr.nq-test.garfusion.500.hybird-npred1.bm25.json",
                             "trivia": "2triviaqa-test/run.dpr.trivia-test.garfusion.500.hybird-npred1.bm25.json"}

    path_out = "/home/zhangxy/QA/QCER/scripts/choose_cases_"  # 修改为 nq/trivia
    settings = {"nq": "GAR Fusion, beta=0.32, gamma=0.1952",
                "trivia": "GAR Fusion, beta=0.76, gamma=0.152"}  # 分别为nq和trivia的参数
    topk_em = 500

    tokenizer = SimpleTokenizer()
    result = defaultdict(dict)
    # generate_file(root_path1 + path_topics[data_name], root_path2 + preds[data_name], path_out + data_name + ".json",
    #               settings[data_name], topk_em, root_path3 + new_retrieval_results[data_name])
    # print("文件已生成!")

    # 开始分析
    """
    Task1：QEvalid配合ans3即可挑选四种case(ans3指的是new retrieval res中是否有答案；只统计top-5的情况)
    Task2：QEvalid配合cases_statistics.py中生成的文件即可
    """
    task_name = "trivia"  # "nq"或者"trivia"
    root_path = "/home/zhangxy/QA/QCER/scripts/"
    case1 = {"nq": "cases_statistics_nq.json", "trivia": "cases_statistics_trivia.json"}
    case2 = {"nq": "choose_cases_nq.json", "trivia": "choose_cases_trivia.json"}
    length = {"nq": 3610, "trivia": 11313}

    # task1
    # with open(root_path + case2[task_name])as f:
    #     data = json.load(f)
    #     for key, value in data.items():
    #         query = data[key]["init_query"]
    #         expansion = data[key]["expansion_terms"]
    #         new_query = data[key]["new_query"]
    #         if not value["QEvalid"]:  # 开关1，控制这两个开关就可以获取4种case
    #             for context in value["new_retrieval_res"]:
    #                 if not context["has_answer"]:  # 开关2
    #                     text = context["text"]
    #                     tmp = {}
    #                     tmp["query"] = query
    #                     tmp["expansion"] = expansion
    #                     tmp["new_query"] = new_query
    #                     tmp["text"] = text
    #                     print("pause")

    # task2
    with open(root_path + case1[task_name]) as f1, open(root_path + case2[task_name]) as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

        flag2 = []
        for key, value in data2.items():
            flag2.append(value["QEvalid"])
        flag11 = data1["ans_initial"]["4"]
        flag12 = data1["ans_new"]["4"]

        cnt1, cnt2, cnt3, cnt4 = 0, 0, 0, 0
        for i in range(length[task_name]):
            a, b, c = flag11[i], flag12[i], flag2[i]
            if not a and b and c:
                cnt1 += 1  # 统计1 从错误→正确，expansion terms正确
            elif not a and b and not c:
                cnt2 += 1  # 统计2 错误→正确，expansion terms错误
            elif a and not b and c:
                cnt3 += 1  # 统计3 从正确→错误，expansion terms正确
            elif a and not b and not c:
                cnt4 += 1  # 统计4 正确→错误，expansion terms错误

        leng = length[task_name]
        print("cnt1: {}\ncnt2: {}\ncnt3: {}\ncnt4: {}\n".format(cnt1 / leng, cnt2 / leng, cnt3 / leng, cnt4 / leng))
