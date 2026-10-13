import numpy as np
import pandas as pd
from markdown_it.rules_core import normalize
from networkx.algorithms.shortest_paths import weighted
from scipy.stats import chi2_contingency
from sklearn.metrics import mutual_info_score

def chi_square_test(
        hard_ct : pd.DataFrame,
) -> dict:
    chi2, p, dof, expected = chi2_contingency(hard_ct.values)
    n = hard_ct.values.sum()
    k = min(hard_ct.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * k)) if n > 0 and k > 0 else 0.0

    return {
        "chi2": chi2,
        "p_value": p,
        "dof": dof,
        "cramers_v": cramers_v,
        "n" : n
    }

class JointMatrix:
    def __init__(
        self,
        lda_result,
        roberta_result,
    ):
        self.lda_result = lda_result
        self.roberta_result = roberta_result
        self.sent_labels = [
            "Negative",
             "Neutral",
             "Positive"
        ]

        self.prob_cols = {
            "Negative": "prob_neg",
            "Neutral": "prob_neu",
            "Positive": "prob_pos"
        }

        self.merged = self.merge(
            self.lda_result,
            self.roberta_result
        )

    def merge(
        self,
        df_topics: pd.DataFrame,
        df_sent: pd.DataFrame,
        on: str = "post_id",
        how: str = "inner",
        topic_col: str = "topic_id",
        topic_prob_col: str = "topic_probs",
        sent_col: str = "sentiment_pred",
        logger=None,
    ):
        need_topics = {on, topic_col, topic_prob_col}
        need_sent = {on, sent_col, "prob_neg", "prob_neu", "prob_pos"}

        missing_t = need_topics - set(df_topics.columns)
        missing_s = need_sent - set(df_sent.columns)

        if missing_t:
            raise KeyError(f"df_topics missing columns: {missing_t}")
        if missing_s:
            raise KeyError(f"df_sent missing columns: {missing_s}")

        df_topics = df_topics.drop_duplicates(subset=[on])
        df_sent = df_sent.drop_duplicates(subset=[on])

        left = df_topics[[on, topic_col, topic_prob_col]].rename(
            columns={topic_col: "topic_id", topic_prob_col: "topic_probs"}
        )
        right = df_sent[[on, sent_col, "prob_neg", "prob_neu", "prob_pos"]].rename(
            columns={sent_col: "sentiment_pred"}
        )
        if "polarity" in df_sent.columns:
            right["polarity"] = df_sent["polarity"].values
        if "confidence" in df_sent.columns:
            right["confidence"] = df_sent["confidence"].values

        merged = left.merge(right, on=on, how=how)

        if logger:
            logger.info(
                f"Joined topics({len(left):,}) × sentiment({len(right):,}) "
                f"→ {len(merged):,} rows (how={how})"
            )
            # coverage diagnostics
            only_topics = set(left[on]) - set(right[on])
            only_sent = set(right[on]) - set(left[on])
            logger.info(f"  post_id only in topics: {len(only_topics):,}")
            logger.info(f"  post_id only in sentiment: {len(only_sent):,}")

        return merged

    def hard_joint(
        self
    ):
        return pd.crosstab(
            self.lda_result["topic_id"],
            self.roberta_result["sentiment_pred"]
        )

    def hard_joint_normalized(
        self
    ):
        copy = pd.crosstab(
            self.lda_result["topic_id"],
            self.roberta_result["sentiment_pred"]
        )

        for lbl in self.sent_labels:
            if lbl not in copy.columns:
                copy[lbl] = 0
        copy = copy[self.sent_labels]

        return copy.div(copy.sum(axis=1 if normalize == "index" else 0), axis=0) \
                if normalize == "index" \
                else copy.div(copy.sum(axis=0), axis=1) if normalize == "columns" \
                else copy / copy.values.sum()

    def soft_fusion(
        self
    ):
        df = self.merged.copy()
        # --- preflight ---
        required = ["topic_id", "topic_probs"] + list(self.prob_cols.values())
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise KeyError(
                f"soft_joint missing columns: {missing}\n"
                f"Available: {df.columns.tolist()}"
            )

        # --- kill duplicate columns (from bad concat/merge) ---
        if df.columns.duplicated().any():
            dupes = df.columns[df.columns.duplicated()].tolist()
            df = df.loc[:, ~df.columns.duplicated(keep="first")]

        rows = []
        for k in sorted(df["topic_id"].unique()):
            sub = df.loc[df["topic_id"] == k]
            if len(sub) == 0:
                continue

            w = sub["topic_probs"].to_numpy(dtype=float)
            denom = w.sum()
            if denom <= 0:
                # all-zero topic posterior — skip
                rows.append(pd.Series(
                    {**{lbl: float("nan") for lbl in self.prob_cols},
                     "n": len(sub)},
                    name=k,
                ))
                continue

            weighted = {}
            for lbl, col in self.prob_cols.items():
                col_series = sub[col]
                if not isinstance(col_series, pd.Series):
                    raise TypeError(
                        f"sub[{col!r}] is {type(col_series).__name__}, expected Series. "
                        f"sub is {type(sub).__name__}, sub.columns = {list(sub.columns)}"
                    )
                vals = col_series.to_numpy(dtype=float)
                weighted[lbl] = float((vals * w).sum() / denom)

            weighted["n"] = int(len(sub))
            rows.append(pd.Series(weighted, name=k))

        return pd.DataFrame(rows)

    def topic_sentiment_mutual_info(
            self,
            topic_col: str = "topic_id",
            sent_col: str = "sentiment_pred"
    ) -> float:
        df = self.merged.copy()
        mi = mutual_info_score(df[topic_col], df[sent_col])
        h_topic = -sum((df[topic_col].value_counts(normalize=True) *
                        np.log(df[topic_col].value_counts(normalize=True) + 1e-12)))
        h_sent = -sum((df[sent_col].value_counts(normalize=True) *
                       np.log(df[sent_col].value_counts(normalize=True) + 1e-12)))
        denom = np.sqrt(h_topic * h_sent)
        return float(mi / denom) if denom > 0 else 0.0