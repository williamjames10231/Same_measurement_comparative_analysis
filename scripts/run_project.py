import logging

from src.data_collection import (
    DataCollection,
    PROJECT_ROOT
)

from src.System_A import (
    pipeline as pipeline_a,
    LDA_model
)

from src.System_B import (
    pipeline as pipeline_b,
)

import pandas as pd
import yaml

def system_a(
    raw_data : pd.DataFrame,
):
    system_a = pipeline_a.Pipeline(raw_data)
    roberta_output = system_a.roberta_model()
    lda_output = system_a.lda_model()
    hard_a, hard_b, soft_a = system_a.fusion(lda_output, roberta_output)

    return hard_a, hard_b, soft_a

def load_config(
    file_path : str,
) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def system_b(
    raw_data : pd.DataFrame,
):
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    cfg = load_config(PROJECT_ROOT / "configs/system_b.yaml")
    system_b = pipeline_b.Pipeline(
        cfg,
        logger,
        raw_data,
        PROJECT_ROOT
    )

    #topic_discovery, topic = system_b.run_topic_discovery()

    topic = pd.read_csv(PROJECT_ROOT / "data/System_B/bulacan_camanava_topic_discovery.csv")
    joint_classification = system_b.run_sentiment_classifier(topic)

    pass

if __name__ == "__main__":
    raw_data = DataCollection()
    raw_data = raw_data.collect_data()
    system_b(raw_data)

    pass
