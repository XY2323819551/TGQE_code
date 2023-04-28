# 合并answer、context、title
import json
from tqdm import *

# 按照sentence、answer、title的顺序混合
# path1 = "/home/zhangxy/QA/QCER/retrieval/runs/nq/tgqe_ex1/sentence_init_text.json"
# path2 = "/home/zhangxy/QA/QCER/retrieval/runs/nq/tgqe_ex1/answer_init_text.json"
# path3 = "/home/zhangxy/QA/QCER/retrieval/runs/nq/tgqe_ex1/title_init_top1_text.json"
# path = "/home/zhangxy/QA/QCER/retrieval/topics/initial_query/nq-test.csv"
# path_out = "/home/zhangxy/QA/QCER/retrieval/runs/nq/tgqe_ex1/fusion_init+DPR.json"
#
# path1 = "/home/zhangxy/QA/QCER/retrieval/runs/trivia/tgqe_ex1/sentence_init_text.json"
# path2 = "/home/zhangxy/QA/QCER/retrieval/runs/trivia/tgqe_ex1/answer_init_text.json"
# path3 = "/home/zhangxy/QA/QCER/retrieval/runs/trivia/tgqe_ex1/title_init_top1_text.json"
# path4 = "/home/zhangxy/QA/QCER/retrieval/runs/trivia/run.dpr.trivia-test.multi.bf.json"
# path = "/home/zhangxy/QA/QCER/retrieval/topics/initial_query/trivia-test.csv"
# path_out = "/home/zhangxy/QA/QCER/retrieval/runs/trivia/tgqe_ex1/fusion_init_text.json"

# path2 = "/home/zhangxy/QA/QCER/retrieval/runs/nq/tgqe_ex1/sentence4_gar_text.json"
# path1 = "/home/zhangxy/QA/QCER/retrieval/runs/nq/tgqe_ex1/title_gar_top1_text.json"
# path = "/home/zhangxy/QA/QCER/retrieval/topics/initial_query/nq-test.csv"
# path_out = "/home/zhangxy/QA/QCER/retrieval/runs/nq/tgqe_ex3/st_gar.json"
# path3 = ""
# path4 = ""

#
# path2 = "/home/zhangxy/QA/QCER/retrieval/runs/trivia/tgqe_ex1/title_gar_top1_text.json"
# path1 = "/home/zhangxy/QA/QCER/retrieval/runs/trivia/tgqe_ex1/answer_gar_11_text.json"
# path = "/home/zhangxy/QA/QCER/retrieval/topics/initial_query/trivia-test.csv"
# path_out = "/home/zhangxy/QA/QCER/retrieval/runs/trivia/tgqe_ex3/at_gar.json"
# path3 = ""
# path4 = ""


def hybrid_v1():
    # 拿出前300条混合，并且是不交叉的方式，比如前333条来自answer，中间的333条来自sentence，后333条来自title
    dict1 = {}
    with open(path1, "r", encoding="utf-8") as f1:
        sentence = json.load(f1)
        for i in range(3610):
            dict1[i] = sentence[str(i)]["contexts"][:333]

    dict2 = {}
    with open(path2, "r", encoding="utf-8") as f2:
        answer = json.load(f2)
        for i in range(3610):
            dict2[i] = answer[str(i)]["contexts"][:333]

    dict3 = {}
    with open(path3, "r", encoding="utf-8") as f3:
        title = json.load(f3)
        for i in range(3610):
            dict3[i] = title[str(i)]["contexts"][:333]

    with open(path, "r", encoding="utf-8") as f:
        question = f.readlines()
        question = [item.strip().split("\t")[0] for item in question]

    data = {}
    for i in range(3610):
        dict_item = {}
        dict_item["question"] = question[i]
        dict_item["answers"] = answer[str(i)]["answers"]
        dict_item["contexts"] = []
        for part1 in dict1[i]:
            dict_item["contexts"].append(part1)
        for part2 in dict2[i]:
            dict_item["contexts"].append(part2)
        for part3 in dict3[i]:
            dict_item["contexts"].append(part3)
        data[str(i)] = dict_item

    with open(path_out, "w", encoding="utf-8") as f_out:
        json.dump(data, f_out, indent=4)
    print("Finished!")


def hybrid_v2_three():
    # 基本可以复现论文的结果，一般来说使用这个就可以啦
    with open(path1) as f1, open(path2) as f2, open(path3) as f3:
        data1 = json.load(f1)
        data2 = json.load(f2)
        data3 = json.load(f3)
        dict_res = {}
        for i in trange(len(data1)):
            item_dict={}
            item_dict["question"] = data1[str(i)]["question"]
            item_dict["answers"] = data1[str(i)]["answers"]
            contexts_list = []
            for j in range(33):
                contexts_list.append(data1[str(i)]["contexts"][j])
                contexts_list.append(data2[str(i)]["contexts"][j])
                contexts_list.append(data3[str(i)]["contexts"][j])
            contexts_list.append(data1[str(i)]["contexts"][33])
            item_dict["contexts"] = contexts_list
            dict_res[str(i)] = item_dict
        with open(path_out, "w", encoding="utf-8") as f_out:
            json.dump(dict_res, f_out)


def hybrid_v2_four():
    # 基本可以复现论文的结果，一般来说使用这个就可以啦
    with open(path1) as f1, open(path2) as f2, open(path3) as f3, open(path4) as f4:
        data1 = json.load(f1)
        data2 = json.load(f2)
        data3 = json.load(f3)
        data4 = json.load(f4)
        dict_res = {}
        for i in trange(len(data1)):
            item_dict={}
            item_dict["question"] = data1[str(i)]["question"]
            item_dict["answers"] = data1[str(i)]["answers"]
            contexts_list = []
            for j in range(250):
                contexts_list.append(data1[str(i)]["contexts"][j])
                contexts_list.append(data2[str(i)]["contexts"][j])
                contexts_list.append(data3[str(i)]["contexts"][j])
                contexts_list.append(data4[str(i)]["contexts"][j])
            item_dict["contexts"] = contexts_list
            dict_res[str(i)] = item_dict
        with open(path_out, "w", encoding="utf-8") as f_out:
            json.dump(dict_res, f_out)


def hybrid_v2_two():
    # 基本可以复现论文的结果，一般来说使用这个就可以啦
    with open(path1) as f1, open(path2) as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)
        dict_res = {}
        for i in trange(len(data1)):
            item_dict={}
            item_dict["question"] = data1[str(i)]["question"]
            item_dict["answers"] = data1[str(i)]["answers"]
            contexts_list = []
            for j in range(500):
                contexts_list.append(data1[str(i)]["contexts"][j])
                contexts_list.append(data2[str(i)]["contexts"][j])
            item_dict["contexts"] = contexts_list
            dict_res[str(i)] = item_dict
        with open(path_out, "w", encoding="utf-8") as f_out:
            json.dump(dict_res, f_out)




# 按照sentence、answer、title的顺序混合
path3 = ""
path4 = ""


# # NQ
# # path1 = "/home/zhangxy/QA/QCER/retrieval/runs/nq/tgqe_ex1/fusion_results/fusion_gar_text.json"
# path1 = "/home/zhangxy/QA/QCER/retrieval/runs/nq/tgqe_ex1/fusion_results/fusion_init_text.json"
# # path1 = "/home/zhangxy/QA/QCER/retrieval/runs/nq/run.dpr.nq-test.bm25.json"
# path2 = "/home/zhangxy/QA/QCER/retrieval/runs/nq/run.dpr.nq-test.multi.bf.json"
# path = "/home/zhangxy/QA/QCER/retrieval/topics/initial_query/nq-test.csv"
# path_out = "/home/zhangxy/QA/QCER/retrieval/runs/nq/tgqe_ex1/fusion_results/init+dpr.json"
#


# Trivia
# path1 = "/home/zhangxy/QA/QCER/retrieval/runs/trivia/tgqe_ex1/fusion_results/fusion_gar_text.json"
# path1 = "/home/zhangxy/QA/QCER/retrieval/runs/trivia/tgqe_ex1/fusion_results/fusion_init_text.json"
path1 = "/home/zhangxy/QA/QCER/retrieval/runs/trivia/run.dpr.trivia-test.bm25.json"
path2 = "/home/zhangxy/QA/QCER/retrieval/runs/trivia/run.dpr.trivia-test.multi.bf.json"
path = "/home/zhangxy/QA/QCER/retrieval/topics/initial_query/trivia-test.csv"
path_out = "/home/zhangxy/QA/QCER/retrieval/runs/trivia/tgqe_ex1/fusion_results/bm25+dpr.json"




def hybrid_v2_two_v2():
    # 基本可以复现论文的结果，一般来说使用这个就可以啦
    with open(path1) as f1, open(path2) as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)
        dict_res = {}
        for i in trange(len(data1)):
            item_dict={}
            item_dict["question"] = data1[str(i)]["question"]
            item_dict["answers"] = data1[str(i)]["answers"]
            contexts_list = []
            for j in range(333):
                contexts_list.append(data1[str(i)]["contexts"][j])
                contexts_list.append(data2[str(i)]["contexts"][3 * j + 1])
                contexts_list.append(data2[str(i)]["contexts"][3 * j + 2])
            item_dict["contexts"] = contexts_list
            dict_res[str(i)] = item_dict
        with open(path_out, "w", encoding="utf-8") as f_out:
            json.dump(dict_res, f_out)


if __name__ == "__main__":
    hybrid_v2_two_v2()
