import logging

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

def lda_diagnotics(
        lda_results,
        vec
) -> pd.DataFrame:
    feature_names = vec.get_feature_names_out()
    print("\n=== LDA Topics ===")

    save_table = pd.DataFrame(columns=["words"])

    for i, comp in enumerate(lda_results.components_):
        top = comp.argsort()[-12:][::-1]
        words = ', '.join(feature_names[j] for j in top)
        save_table.loc[i] = words
        print(f"Topic {i}: {words}")

    return save_table


class LDAModel:
    def __init__(
            self,
            corpus : pd.DataFrame,
    ) -> None:
        self.copy = corpus.copy()
        self.corpus = self.copy[self.copy["disaster_event"] != "None"]["text"].dropna().astype(str).tolist()

        self.STOPWORDS = {
            # Filipino particles
            "ang", "ng", "mga", "sa", "at", "ay", "na", "po", "opo", "yung", "'yung", "naman",
            "kasi", "para", "rin", "din", "lang", "pa", "ba", "kaya", "namin", "natin", "kami",
            "tayo", "sila", "siya", "ito", "iyan", "iyon", "dito", "diyan", "doon", "may",
            "meron", "wala", "hindi", "oo", "o", "e", "eh", "ah", "oh", "uy",
            # English
            "the", "a", "an", "is", "are", "was", "were", "to", "of", "in", "on", "for",
            "and", "or", "but", "with", "as", "at", "by",
            # ⚠️ ADD: geographic noise that's breaking topic separation
            "brgy", "barangay", "gen", "luna", "malabon", "navotas", "valenzuela",
            "caloocan", "hagonoy", "calumpit", "bulacan", "camanava",
            # ⚠️ ADD: conversational filler that created Topic 9
            "yan", "kahit", "amin", "totoo", "actually", "talaga", "talagang",
            "sana", "kita", "same", "naiintindihan",
        }

        self.N_topics = 12

    def count_vectorizer(
            self
    ):
        vec = CountVectorizer(
            max_df=0.85,
            min_df=5,
            ngram_range=(1, 2),
            stop_words=list(self.STOPWORDS),
            token_pattern=r"(?u)\b\w+\b"
        )

        dtm = vec.fit_transform(self.corpus)

        return dtm, vec

    def run_lda(
            self,
            dtm,
            vec
    ):
        copy = pd.DataFrame(self.corpus).copy()
        copy = copy.rename(columns={0: "text"})


        lda = LatentDirichletAllocation(
            n_components=self.N_topics,
            random_state=42,
            learning_method='batch',
            max_iter=100,
        )

        lda.fit(dtm)
        topic_probs = lda.transform(
            vec.transform(copy["text"].fillna("").astype(str))
        )
        copy["post_id"] = self.copy["post_id"]
        copy["topic_id"] = topic_probs.argmax(axis=1)
        copy["topic_probs"] = topic_probs.max(axis=1)

        return copy, lda

    def calculate_umass_coherence(
        self,
        top_word_indices,
        X_bool
    ):
        coherence = 0.0
        num_words = len(top_word_indices)

        for i in range(1, num_words):
            w_i = top_word_indices[i]
            d_wi = np.sum(X_bool[:, w_i])

            for j in range(0, i):
                w_j = top_word_indices[j]
                d_wi_wj = np.sum(X_bool[:, w_i].multiply(X_bool[:, w_j]))
                coherence += np.log((d_wi_wj + 1.0) / d_wi)

        return coherence

    def coherence_sweep(
        self,
        dtm,
        vec
    ):
        X_bool = (dtm > 0).astype(int)
        feature_names = vec.get_feature_names_out()
        k_values = range(4, 15)
        coherence_scores = []

        for k in k_values:
            lda = LatentDirichletAllocation(
                n_components=k,
                random_state=42,
                learning_method='batch',
                max_iter=100,
            )

            lda.fit(dtm)

            top_n_words = 10
            topic_coherences = []

            for topic in lda.components_:
                top_words_ind = topic.argsort()[:-top_n_words - 1:-1]
                score = self.calculate_umass_coherence(top_words_ind, X_bool)
                topic_coherences.append(score)

            coherence_scores.append(np.mean(topic_coherences))
            print(f"K={k} | Mean UMass Coherence: {coherence_scores[-1]:.4f}")

        plt.figure(figsize=(8, 5))
        plt.plot(k_values, coherence_scores, marker='o', color='r')
        plt.title("UMass Coherence vs Number of Topics K")
        plt.xlabel("Number of Topics K")
        plt.ylabel("UMass Coherence Score (Closer to 0 is better)")
        plt.grid(True)
        plt.show()

        return coherence_scores

