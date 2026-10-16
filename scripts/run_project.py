import logging
import pathlib

from src.data_collection import (
    DataCollection,
    PROJECT_ROOT
)

from src.System_A import (
    pipeline as pipeline_a,
    LDA_model,
)

from src.System_A.joint_matrix import chi_square_test as chi_square_test

from src.System_B import (
    pipeline as pipeline_b,
    joint_matrix_llm as joint_matrix_b,
)

import pandas as pd
import yaml

def system_a(
    raw_data : pd.DataFrame,
    is_testing_k,
    PROJECT_ROOT : pathlib.Path
):
    system_a = pipeline_a.Pipeline(raw_data)

    if is_testing_k:
        coherence_scores = system_a.test_k()

        pd.DataFrame([coherence_scores]).to_csv(
            PROJECT_ROOT / "data/system_a/bulacan_camanava_coherence_scores.csv",
        )

        return None
    else:
        lda_output, diagnostics = system_a.lda_model()

        lda_output.to_csv(
            PROJECT_ROOT / "data/system_a/bulacan_camanava_lda_enriched.csv",
        )

        diagnostics.to_csv(
            PROJECT_ROOT / "data/system_a/bulacan_camanava_lda_topic_word_enriched.csv"
        )

        roberta_output = system_a.roberta_model()

        roberta_output.to_csv(
            PROJECT_ROOT / "data/system_a/bulacan_camanava_roberta_enriched.csv",
        )

        hard_a, hard_b, soft_a = system_a.fusion(lda_output, roberta_output)

        hard_a.to_csv(
            PROJECT_ROOT / "data/system_a/bulacan_camanava_hard_matrix_enriched.csv",
        )

        hard_b.to_csv(
            PROJECT_ROOT / "data/system_a/bulacan_camanava_hard_matrix_norm_enriched.csv",
        )

        soft_a.to_csv(
            PROJECT_ROOT / "data/system_a/bulacan_camanava_soft_matrix_enriched.csv",
        )

        diagnostics = chi_square_test(hard_a)

        pd.DataFrame([diagnostics]).to_csv(
            PROJECT_ROOT / "data/system_a/bulacan_camanava_diagnostics.csv",
        )

        return hard_a, hard_b, soft_a, diagnostics

def load_config(
    file_path : str,
) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def system_b(
    raw_data : pd.DataFrame,
):
    logger = logging.getLogger(__name__)
    cfg = load_config(PROJECT_ROOT / "configs/system_b.yaml")
    system_b = pipeline_b.Pipeline(
        cfg,
        logger,
        raw_data,
        PROJECT_ROOT
    )

    topic_discovery, topic = system_b.run_topic_discovery()

    topic = pd.read_csv(PROJECT_ROOT / "data/System_B/bulacan_camanava_topic_discovery.csv")
    #joint_classification = system_b.run_sentiment_classifier(topic)
    joint_classification = pd.read_csv(PROJECT_ROOT / "data/System_B/bulacan_camanava_sentiment_classification.csv")

    joint_matrix = joint_matrix_b.JointMatrix(
        topic,
        joint_classification,
        PROJECT_ROOT
    )
    output, norm = joint_matrix.compute_matrices()
    readings = chi_square_test(output)
    pass

if __name__ == "__main__":
    raw_data = DataCollection()
    raw_data = raw_data.collect_data()
    system_b(raw_data)
    pass
    system_a(
        raw_data,
        False,
        PROJECT_ROOT
    )
    pass
