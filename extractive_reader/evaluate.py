from typing import List, Optional, Dict
from tqdm import tqdm
import string
import regex as re

from .retrieval import RetrievalExample
from .base import Reader

__all__ = ['ReaderEvaluator']

class ReaderEvaluator:
    """Class for evaluating a reader.
    Takes in a list of examples (query, texts, ground truth answers),
    predicts a list of answers using the Reader passed in, and
    collects the exact match accuracies between the best answer and
    the ground truth answers given in the example.
    Exact match scoring used is identical to the DPR repository.
    """

    def __init__(
        self,
        reader: Reader,
    ):
        self.reader = reader

    def evaluate(
        self,
        examples: List[RetrievalExample],
        topk_em: List[int] = [50],
        rider_predictions: Optional[Dict[str, List[str]]] = None,
    ):
        ems = {str(setting): {k: [] for k in topk_em} for setting in self.reader.span_selection_rules}
        for example in tqdm(examples):
            answers = self.reader.predict(example.question, example.contexts, topk_em)  # answer:Dict[int, List[Answer]]
            ground_truth_answers = example.ground_truth_answers
            topk_prediction = {str(setting): {} for setting in self.reader.span_selection_rules}

            for setting in self.reader.span_selection_rules:
                for k in topk_em:
                    best_answer = answers[str(setting)][k][0].text
                    em_hit = max([ReaderEvaluator.exact_match_score(best_answer, ga) for ga in ground_truth_answers])
                    ems[str(setting)][k].append(em_hit)
                    topk_prediction[f'{str(setting)}'][f'top{k}'] = best_answer

            if rider_predictions is not None:
                tmp_pred1 = {}
                for setting in self.reader.span_selection_rules:
                    tmp_pred2 = {}
                    for k in topk_em:
                        ans_length = len(answers[str(setting)][k])
                        top10_answers = [answers[str(setting)][k][j].text for j in range(ans_length)]
                        tmp_pred2[k] = top10_answers
                    tmp_pred1[str(setting)] = tmp_pred2
                rider_predictions[example.question.text] = tmp_pred1
        print("Inference Finished!")
        return ems

    @staticmethod
    def exact_match_score(prediction, ground_truth):
        return ReaderEvaluator._normalize_answer(prediction) == ReaderEvaluator._normalize_answer(ground_truth)

    @staticmethod
    def _normalize_answer(s):
        def remove_articles(text):
            return re.sub(r'\b(a|an|the)\b', ' ', text)

        def white_space_fix(text):
            return ' '.join(text.split())

        def remove_punc(text):
            exclude = set(string.punctuation)
            return ''.join(ch for ch in text if ch not in exclude)

        def lower(text):
            return text.lower()

        return white_space_fix(remove_articles(remove_punc(lower(s))))
