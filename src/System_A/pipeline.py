import numpy as np
import pandas as pd

from src.System_A.LDA_model import (
    LDAModel,
    lda_diagnotics
)

from src.System_A.roberta_classifier import RobertaClassifier
from src.System_A.joint_matrix import  (
    JointMatrix,
    chi_square_test
)

class Pipeline:
    def __init__(
            self,
            given_data : pd.DataFrame
    ) -> None:
        self.data = given_data
        self.RoBERTa_model_name = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
        self.batch_size = 64
        self.max_len = 128
        self.csv_out = "../bulacan_camanava_roberta_enriched.csv"

    def roberta_model(
            self
    ) -> pd.DataFrame:
        roberta_model = RobertaClassifier(self.data)
        copy = roberta_model.roberta_model()
        roberta_model.roberta_diagnostics(copy)
        return copy


    def lda_model(
            self
    ) -> pd.DataFrame:
        lda_model = LDAModel(self.data)
        dtm, count_vec = lda_model.count_vectorizer()
        lda_result,lda = lda_model.run_lda(
            dtm,
            count_vec
        )

        lda_diagnotics(
            lda,
            count_vec
        )

        return lda_result

    def fusion(
            self,
            lda_result: pd.DataFrame,
            roberta_result: pd.DataFrame
    ):
        joint_matrix = JointMatrix(
            lda_result,
            roberta_result
        )

        hard_matrix, hard_matrix_norm = joint_matrix.hard_joint(), joint_matrix.hard_joint_normalized()
        soft_matrix = joint_matrix.soft_fusion()

        print(chi_square_test(hard_matrix))
        print(joint_matrix.topic_sentiment_mutual_info())

        hard_matrix.to_csv("../data/system_a/bulacan_camanava_hard_matrix_enriched.csv")
        hard_matrix_norm.to_csv("../data/system_a/bulacan_camanava_hard_matrix_norm_enriched.csv")
        soft_matrix.to_csv("../data/system_a/bulacan_camanava_soft_matrix_enriched.csv")

        return hard_matrix, hard_matrix_norm, soft_matrix
