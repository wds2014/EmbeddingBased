from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import numpy as np

__all__ = [
    "average_sentence_level",
    "average_corpus_level",
    "extrema_sentence_level",
    "extrema_corpus_level",
]

_EPSILON = 0.00000000001


def _compute_statistics(scores):
    """
    Compute various statistics from a list of scores.
    The scores come from evaluating a list of sentence pairs.
    The function combines them by mean and standard derivation.

    :param scores: a list of float.
    :return: a 3-tuple: mean, <unk>, standard derivation.
    """
    return np.mean(scores), 1.96 * np.std(scores) / len(scores), np.std(scores)


def _cosine_similarity(a, b):
    """
    Return the cosine similarity of two vector a and b.

    :param a: ndarray of 1D.
    :param b: ndarray of 1D.
    :return: float.
    """
    return np.dot(a, b) / np.linalg.norm(a) / np.linalg.norm(b)


def _embedding_sum(sentence, embeddings):
    """
    Return the sum of embeddings of words in sentence.

    :param sentence: a list of tokens.
    :param embeddings: a KeyedVectors.
    :return: a 1D ndarray of len `embeddings.vector_size`.
    """
    total = sum(embeddings[word] for word in sentence if word in embeddings)
    if np.linalg.norm(total) < _EPSILON:
        # If none of the words has embeddings, return all holes.
        return np.zeros((embeddings.vector_size,))
    return total


def _get_average(sentence, embeddings):
    total = _embedding_sum(sentence, embeddings)
    return total / np.linalg.norm(total)


def average_sentence_level(hypothesis_sentence, reference_sentence, embeddings):
    """
    Compute Average on sentence level.

    :param hypothesis_sentence:
    :param reference_sentence:
    :param embeddings:
    :return:
    """
    return _cosine_similarity(
        a=_get_average(hypothesis_sentence, embeddings),
        b=_get_average(reference_sentence, embeddings),
    )


def average_corpus_level(hypothesis_corpus, reference_corpus, embeddings):
    """
    Compute Average on corpus level.

    :param hypothesis_corpus:
    :param reference_corpus:
    :param embeddings:
    :return:
    """
    assert len(hypothesis_corpus) == len(reference_corpus)
    scores = []

    for hypothesis, reference in zip(hypothesis_corpus, reference_corpus):
        X = _embedding_sum(hypothesis, embeddings)
        Y = _embedding_sum(reference, embeddings)
        # if none of the words in ground truth have embeddings, skip
        if np.linalg.norm(X) < _EPSILON:
            continue

        # if none of the words have embeddings in response, count result as zero
        if np.linalg.norm(Y) < _EPSILON:
            scores.append(0)
            continue

        # Normalize to unit vectors.
        X /= np.linalg.norm(X)
        Y /= np.linalg.norm(Y)
        scores.append(_cosine_similarity(X, Y))

    return _compute_statistics(scores)


def _get_extrema(vectors):
    """
    Compute the Extrema vector from a list of vectors.

    :param vectors: a list of 1D vectors all having the same shape.
    :return: the Extrema vector.
    """
    max_values = np.max(vectors, axis=0)
    min_values = np.min(vectors, axis=0)
    return np.array([
        min_v if np.abs(min_v) > max_v else max_v
        for min_v, max_v in zip(min_values, max_values)
    ])


def _map_to_embeddings(words, embeddings):
    """
    Map each word in words to its embedding skipping any OOV words.
    Thus the dimension of words may not match that of the returned list.

    :param words: a list of strings.
    :param embeddings: a gensim KeyedVectors.
    :return:  a list of ndarrays.
    """
    return [embeddings[word] for word in words if word in embeddings]


def extrema_sentence_level(hypothesis_sentence, reference_sentence, embeddings):
    """
    Compute Extrema on sentence level.

    :param hypothesis_sentence:
    :param reference_sentence:
    :param embeddings:
    :return:
    """
    hypothesis = _map_to_embeddings(hypothesis_sentence, embeddings)
    reference = _map_to_embeddings(reference_sentence, embeddings)
    return _cosine_similarity(
        a=_get_extrema(hypothesis),
        b=_get_extrema(reference),
    )


def extrema_corpus_level(hypothesis_corpus, reference_corpus, embeddings):
    """
    Compute Extrema on corpus level.

    :param hypothesis_corpus:
    :param reference_corpus:
    :param embeddings:
    :return:
    """
    scores = []
    for hypothesis, reference in zip(hypothesis_corpus, reference_corpus):
        X = _map_to_embeddings(hypothesis, embeddings)
        Y = _map_to_embeddings(reference, embeddings)

        if np.linalg.norm(X) < _EPSILON:
            continue
        if np.linalg.norm(Y) < _EPSILON:
            scores.append(0)
            continue

        value = _cosine_similarity(_get_extrema(hypothesis), _get_extrema(reference))
        scores.append(value)

    return _compute_statistics(scores)


def greedy_match_sentence_level(hypothesis_sentence, reference_sentence, embeddings):
    pass
