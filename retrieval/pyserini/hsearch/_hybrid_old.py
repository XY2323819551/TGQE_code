#
# Pyserini: Reproducible IR research with sparse and dense representations
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
This module provides Pyserini's hybrid searcher by Dense + Sparse
"""

from typing import List, Dict
from pyserini.search import SimpleSearcher
from pyserini.dsearch import SimpleDenseSearcher, DenseSearchResult
import numpy as np


class HybridSearcher:
    """Hybrid Searcher for dense + sparse

        Parameters
        ----------
        dense_searcher : SimpleDenseSearcher
        sparse_searcher : SimpleSearcher
    """

    def __init__(self, dense_searcher, sparse_searcher):
        self.dense_searcher = dense_searcher
        self.sparse_searcher = sparse_searcher

    def search(self, query: str, k: int = 10, alpha: float = 0.1) -> List[DenseSearchResult]:
        dense_hits = self.dense_searcher.search(query, k)
        sparse_hits = self.sparse_searcher.search(query, k)
        return self._hybrid_results(dense_hits, sparse_hits, alpha, k)

    def batch_search(self, queries: List[str], q_ids: List[str], k: int = 10, threads: int = 1, alpha: float = 0.1) \
            -> Dict[str, List[DenseSearchResult]]:
        dense_result = self.dense_searcher.batch_search(queries, q_ids, k, threads)
        sparse_result = self.sparse_searcher.batch_search(queries, q_ids, k, threads)
        hybrid_result = {
            key: self._hybrid_results(dense_result[key], sparse_result[key], alpha, k)
            for key in dense_result
        }
        return hybrid_result

    @staticmethod
    def _hybrid_results(dense_results, sparse_results, alpha, k):
        dense_hits = {hit.docid: hit.score for hit in dense_results}
        sparse_hits = {hit.docid: hit.score for hit in sparse_results}
        hybrid_result = []

        # 两者分别归一化
        # dense_score, sparse_score, dense_docid, sparse_docid= [], [], [], []
        # for hit in dense_results:
        #     dense_score.append(hit.score)
        #     dense_docid.append(hit.docid)
        # for hit in sparse_results:
        #     sparse_score.append(hit.score)
        #     sparse_docid.append(hit.docid)
        # dense_mean = np.array(dense_score).mean()
        # dense_std = np.array(dense_score).std()
        # sparse_mean = np.array(sparse_score).mean()
        # sparse_std = np.array(sparse_score).std()
        # norm_dense_score = (dense_score - dense_mean) / dense_std
        # norm_sparse_score = (sparse_score - sparse_mean) / sparse_std
        # dense_hits = dict(zip(dense_docid, norm_dense_score))
        # sparse_hits = dict(zip(sparse_docid, norm_sparse_score))
        # hybrid_result = []

        # 两者放在一块归一化
        # dense_score, sparse_score, dense_docid, sparse_docid= [], [], [], []
        # all_score=[]
        # for hit in dense_results:
        #     dense_score.append(hit.score)
        #     all_score.append(hit.score)
        #     dense_docid.append(hit.docid)
        # for hit in sparse_results:
        #     sparse_score.append(hit.score)
        #     all_score.append(hit.score)
        #     sparse_docid.append(hit.docid)
        # mean = np.array(all_score).mean()
        # std = np.array(all_score).std()
        # norm_dense_score = (dense_score - mean) / std
        # norm_sparse_score = (sparse_score - mean) / std
        # dense_hits = dict(zip(dense_docid, norm_dense_score))
        # sparse_hits = dict(zip(sparse_docid, norm_sparse_score))
        # hybrid_result = []

        min_dense_score = min(dense_hits.values()) if len(dense_hits) > 0 else 0
        min_sparse_score = min(sparse_hits.values()) if len(sparse_hits) > 0 else 0
        for doc in set(dense_hits.keys()) | set(sparse_hits.keys()):
            if doc not in dense_hits:
                score = alpha * sparse_hits[doc] + min_dense_score
            elif doc not in sparse_hits:
                score = alpha * min_sparse_score + dense_hits[doc]
            else:
                score = max(sparse_hits[doc], dense_hits[doc])
            hybrid_result.append(DenseSearchResult(doc, score))
        return sorted(hybrid_result, key=lambda x: x.score, reverse=True)[:k]
