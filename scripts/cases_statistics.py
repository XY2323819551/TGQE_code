import json
from collections import defaultdict

"""
这个文件用来统计the initial retrieval results和the new retrieval results文件中不同k值对应的两种情况：
（1）the initial retrieval results中检索错误的case，the initial retrieval results中检索正确了
（2）the initial retrieval results中检索正确的case，the initial retrieval results中检索错误了
"""


def statistic(path_list, task_names, nums):
    for ith in range(len(path_list)):
        path = path_list[ith]
        task_name = task_names[ith]
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for qid in list(data.keys()):
            flag = False
            contexts = data[qid]['contexts']
            for k, context in enumerate(contexts):
                if context["has_answer"]:
                    flag = True
                    for num in nums:
                        if num < k:
                            res_dict[task_name][num].append(0)
                        else:
                            res_dict[task_name][num].append(1)
                    break
            if not flag:
                for num in nums:
                    res_dict[task_name][num].append(0)


def analysis(data, length, nums):
    # Incorrect->Correct; Incorrect->Correct
    results = defaultdict(list)
    for k in nums:
        results[str(k)] = [0, 0]
        for i in range(length):
            if not data["ans_initial"][str(k)][i] and data["ans_new"][str(k)][i]:
                results[str(k)][0] += 1
            elif data["ans_initial"][str(k)][i] and not data["ans_new"][str(k)][i]:
                results[str(k)][1] += 1
        print("top-{}，Incorrect->Correct:{}".format(k + 1, results[str(k)][0] / length))
        print("top-{}，Correct->Incorrect:{}".format(k + 1, results[str(k)][1] / length))
        print("\n")
    return results


if __name__ == "__main__":
    # ① generate "res_dict" file
    res_dict = {"ans_initial": defaultdict(list), "ans_new": defaultdict(list)}
    nums = [0, 4, 9, 19, 49, 99, 499, 999]
    length = 11313  # nq:3610, trivia:11313
    # root_path = "/home/zhangxy/QA/castorini/pyserini/runs/2triviaqa-test/"
    #
    # path_list = [root_path + "run.dpr.trivia-test.bm25.json",
    #              root_path + "run.dpr.trivia-test.garfusion.500.hybird-npred1.bm25.json"]
    # task_names = ["ans_initial", "ans_new"]
    # statistic(path_list, task_names, nums)
    #
    # # 打印信息，查看res_dict的正确性
    # for num in nums:
    #     print("top-{} accuracy : {}".format(num + 1, sum(res_dict["ans_initial"][num]) / length))
    # print("********************************************************")
    # for num in nums:
    #     print("top-{} accuracy : {}".format(num + 1, sum(res_dict["ans_new"][num]) / length))
    # with open("/home/zhangxy/QA/QCER/scripts/cases_statistics_trivia.json", "w", encoding="utf-8") as f_out:
    #     json.dump(res_dict, f_out)
    # print("finished!")

    # ②进行信息的统计
    with open("/home/zhangxy/QA/QCER/scripts/cases_statistics_trivia.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    results = analysis(data, length, nums)
