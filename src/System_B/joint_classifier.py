import json
import pandas as pd
from tqdm import tqdm
from collections import Counter
from src.System_B.prompts import JOINT_SYSTEM, JOINT_USER
from src.System_B.llmclient import extract_json_array


class JointClassifier:
    def __init__(self, llm, cfg: dict, logger=None) -> None:
        self.llm = llm
        self.cfg = cfg
        self.log = logger
        self.valid_sentiments = {"POS", "NEG", "NEU"}

    def classify(self, df: pd.DataFrame, taxonomy: pd.DataFrame) -> pd.DataFrame:
        df = pd.DataFrame(df)
        df = df[1:50] #input control
        df.columns = ["text"]
        valid_labels = set()
        topic_lines = []
        for t in taxonomy.itertuples():
            label = t.label.strip().lower()
            desc = t.keywords.strip()
            valid_labels.add(label)
            topic_lines.append(f"- {label}: {desc}")

        topic_list_str = "\n".join(topic_lines)

        results = []
        total_rows = len(df)
        parse_failures = 0

        sent_counter = Counter()
        topic_counter = Counter()

        if self.log:
            pass
            #self.log.info(f"Stage 2: Starting joint classification for {total_rows} rows.")
            #self.log.info(f"Valid topics: {list(valid_labels)}")

        pbar = tqdm(
            df.iterrows(),
            total=total_rows,
            desc="Classifying Rows",
            unit="doc"
        )

        for idx, row in pbar:
            text = str(row.get("text", ""))
            if not text or text == "nan":
                results.append({"sentiment": "NEU", "topic": "unknown", "raw_output": "EMPTY_TEXT"})
                continue

            # Format prompt
            prompt_usr = JOINT_USER.format(
                topic_list_with_descriptions=topic_list_str,
                text=text[:1000]  # Truncate to protect context window
            )

            try:
                raw_output = self.llm.generate(
                    JOINT_SYSTEM,
                    prompt_usr,
                    max_new_tokens=150  # Enough for a short JSON object
                )

                # Parse JSON
                parsed = extract_json_array(raw_output)

                if parsed and isinstance(parsed, dict):
                    sent = str(parsed.get("sentiment", "NEU")).strip().upper()
                    topic = str(parsed.get("topic", "")).strip().lower()

                    sent = sent if sent in self.valid_sentiments else "NEU"
                    topic = topic if topic in valid_labels else "unknown_topic"

                    results.append({"sentiment": sent, "topic": topic, "raw_output": ""})
                    sent_counter.update([sent])
                    topic_counter.update([topic])
                else:
                    parse_failures += 1
                    results.append({"sentiment": "PARSE_ERR", "topic": "PARSE_ERR", "raw_output": raw_output[:100]})

            except Exception as e:
                parse_failures += 1
                results.append({"sentiment": "SYS_ERR", "topic": "SYS_ERR", "raw_output": str(e)[:100]})

            processed = len(results)
            if processed % max(1, total_rows // 10) == 0 or processed == total_rows:
                pct = (processed / total_rows) * 100
                fail_rate = (parse_failures / processed) * 100

                # Update tqdm postfix with live stats
                pbar.set_postfix({
                    "Fail%": f"{fail_rate:.1f}%",
                    "Top_Sent": sent_counter.most_common(1)[0][0] if sent_counter else "N/A",
                    "Top_Topic": topic_counter.most_common(1)[0][0] if topic_counter else "N/A"
                })

                if self.log:
                    pass
                    #self.log.info(f"[{pct:.0f}%] Processed: {processed}/{total_rows} | "
                    #              f"Parse Failures: {parse_failures} ({fail_rate:.1f}%) | "
                    #              f"Sentiment Dist: {dict(sent_counter)}")

        pbar.close()

        res_df = pd.DataFrame(results)
        output_df = pd.concat([df.reset_index(drop=True), res_df], axis=1)

        if self.log:
            pass
            #self.log.info("Stage 2 Complete. Final Sentiment Distribution:")
            #self.log.info(f"\n{output_df['sentiment'].value_counts().to_string()}")
            #self.log.info("Final Topic Distribution:")
            #self.log.info(f"\n{output_df['topic'].value_counts().to_string()}")

        return output_df