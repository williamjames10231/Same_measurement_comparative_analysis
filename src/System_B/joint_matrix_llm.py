import pandas as pd
from matplotlib import path


class JointMatrix:
    def __init__(
        self,
        topic_discovery_result : pd.DataFrame,
        joint_classifier_result: pd.DataFrame,
        PROJCT_ROOT : path
    ) -> None:
        self.topic_discovery_result = topic_discovery_result
        self.joint_classifier_result = joint_classifier_result
        self.joint_classifier_result = joint_classifier_result.dropna(subset=["topic"])
        self.PROJECT_ROOT = PROJCT_ROOT

    def compute_hard_matrix(
        self
    ) -> pd.DataFrame:
        hard_matrix = pd.crosstab(
            index=self.joint_classifier_result["topic"],
            columns=self.joint_classifier_result["sentiment"],
            margins=True,
            margins_name="total",
        )

        return hard_matrix

    def compute_hard_matrix_normalized(
        self
    ) -> pd.DataFrame:
        hard_matrix = pd.crosstab(
            index=self.joint_classifier_result["topic"],
            columns=self.joint_classifier_result["sentiment"],
            margins=True,
            margins_name="total",
            normalize=True,
        )

        return hard_matrix

    def compute_matrices(
        self
    ):
        hard_matrix = self.compute_hard_matrix()
        hard_matrix_normalized = self.compute_hard_matrix_normalized()
        hard_matrix.to_csv(self.PROJECT_ROOT / "data/System_B/bulacan_camanava_hard_matrix_enriched.csv")
        hard_matrix_normalized.to_csv(self.PROJECT_ROOT / "data/System_B/bulacan_camanava_hard_matrix_norm_enriched.csv")

        return hard_matrix, hard_matrix_normalized
