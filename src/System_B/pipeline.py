from unittest import result

import pandas as pd
from pathlib import Path

from pip._internal.commands import index

from src.System_B.llmclient import LLMClient
from src.System_B.topic_discovery import TopicDiscovery
from src.System_B.joint_classifier import JointClassifier

class Pipeline:
    def __init__(
        self,
        cfg,
        logger,
        given_data : pd.DataFrame,
        parent_directory : Path
    ) -> None:
        self.cfg = cfg
        self.logger = logger

        logger.info("System B: loading raw data")
        self.df = given_data.copy()
        logger.info(f"Rows: {len(self.df):,}")
        self.PARENT_DIRECTORY = parent_directory
        self.llm = LLMClient(cfg, logger)

    def run_topic_discovery(
        self
    ):
        discovery = TopicDiscovery(
            self.llm,
            self.cfg,
            self.logger
        )

        topics = discovery.discover(
            self.df,
            sample_n=self.cfg["llm_topics"]["discovery_sample"]
        )

        self.logger.info(f"Topics: {topics}")
        decoy = pd.DataFrame(topics)
        out = pd.DataFrame(
            {
                "topic_id": range(len(topics)),
                "label": decoy["label"],
                "description": decoy["description"],
            }
        )


        out.to_csv(
            self.PARENT_DIRECTORY / "data/System_B/bulacan_camanava_topic_discovery.csv",
            index=False
        )

        pd.Series(decoy["label"]).to_csv(
            self.PARENT_DIRECTORY / "data/System_B/bulacan_camanava_topics.csv",
            index=False
        )

        return out, decoy["label"]

    def run_sentiment_classifier(
        self,
        topics,
    ):
        classifier = JointClassifier(
            self.llm,
            topics,
            self.cfg,
        )

        self.logger.info(f"Classifying {len(self.df):,}rows (this is the slow part)...")
        out, result = None, None

        result = classifier.classify(self.df["text"].tolist(), topics)
        out = pd.concat([self.df[["post_id"]].reset_index(drop=True),
                     result.reset_index(drop=True)], axis=1)
        out.to_csv(
            self.PARENT_DIRECTORY / "data/System_B/bulacan_camanava_sentiment_classification.csv",
            index=False
        )

        return out, result

    def joint_helper(
        self,
        out
    ):
        lda_like = out[["post_id", "topic_id", "topic_prob", "topic_label"]].copy()
        lda_like.to_csv(self.PARENT_DIRECTORY / "data/processed/system_b_lda_topics.csv", index=False)

        sent_like = out[["post_id", "sentiment_pred", "prob_neg", "prob_neu", "prob_pos"]].copy()
        sent_like["polarity"] = sent_like["prob_pos"] - sent_like["prob_neg"]
        sent_like["confidence"] = sent_like[["prob_neg", "prob_neu", "prob_pos"]].max(axis=1)
        sent_like.to_csv(self.PARENT_DIRECTORY / "data/processed/system_b_roberta_sentiment.csv", index=False)

        self.logger.info("System B done. Outputs match System A schema.")
        return {"topics": lda_like, "sentiment": sent_like}
