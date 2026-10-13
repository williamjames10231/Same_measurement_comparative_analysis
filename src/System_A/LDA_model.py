import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer


def lda_diagnotics(
        lda_results,
        vec
) -> None:
    feature_names = vec.get_feature_names_out()
    print("\n=== LDA Topics ===")

    save_table = pd.DataFrame(columns=["words"])

    for i, comp in enumerate(lda_results.components_):
        top = comp.argsort()[-12:][::-1]
        words = ', '.join(feature_names[j] for j in top)
        save_table.loc[i] = words
        print(f"Topic {i}: {words}")

    save_table.to_csv("../data/system_a/bulacan_camanava_lda_topic_word_enriched.csv")


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

        self.N_topics = 6

        self.csv_out = "../data/system_a/bulacan_camanava_lda_enriched.csv"

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
            max_iter=20,
        )

        lda.fit(dtm)
        topic_probs = lda.transform(
            vec.transform(copy["text"].fillna("").astype(str))
        )
        copy["post_id"] = self.copy["post_id"]
        copy["topic_id"] = topic_probs.argmax(axis=1)
        copy["topic_probs"] = topic_probs.max(axis=1)

        copy.to_csv(
            self.csv_out,
            index=False
        )

        return copy, lda

