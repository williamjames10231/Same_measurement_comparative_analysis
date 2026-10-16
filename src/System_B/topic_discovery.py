import pandas as pd

from src.System_B.llmclient import extract_json_array
from src.System_B.prompts import (
    TOPIC_DISCOVERY_SYSTEM,
    TOPIC_DISCOVERY_USER
)

class TopicDiscovery:
    def __init__(
            self,
            llm,
            cfg: dict,
            logger=None,
    ) -> None:
        self.llm = llm
        self.cfg = cfg["llm_topics"]
        self.log = logger

    #200 topics
    def discover(self, df: pd.DataFrame, sample_n: int = 500) -> list[dict]:
        if "disaster_event" in df.columns:
            n_events = df["disaster_event"].nunique()
            per_event = max(1, sample_n // n_events)
            sample = (
                df.groupby("disaster_event", group_keys=False)
                .apply(lambda g: g.sample(min(len(g), per_event), random_state=42))
                .head(sample_n)
            )
        else:
            sample = df.sample(min(len(df), sample_n), random_state=42)

        if self.log:
            self.log.info(f"Stage 1: Discovering topics from {len(sample)} sampled docs via batch JSON synthesis")

        documents_block = "\n".join(
            [f"[{i+1}] {str(text)[:sample_n]}" for i, text in enumerate(sample["text"].tolist())]
        )
        self.log.info(documents_block)

        prompt_sys = TOPIC_DISCOVERY_SYSTEM.format(n_topics=self.cfg["n_topics"])
        prompt_usr = TOPIC_DISCOVERY_USER.format(
            n_docs=len(sample),
            documents_block=documents_block,
            n_topics=self.cfg["n_topics"]
        )

        try:
            raw_output = self.llm.generate(prompt_sys, prompt_usr, max_new_tokens=2048)
        except Exception as e:
            if self.log:
                self.log.error(f"LLM failed during topic discovery: {e}")
            return self._fallback_taxonomy()

        parsed = extract_json_array(raw_output)

        if not parsed or not isinstance(parsed, list):
            if self.log:
                self.log.warning(f"Failed to parse JSON taxonomy. Raw output:\n{raw_output[:500]}")
            return self._fallback_taxonomy()

        canonical = []
        for item in parsed:
            if isinstance(item, dict) and "label" in item:
                label = str(item["label"]).strip().lower()
                desc = str(item.get("keywords", "")).strip()
                if 2 <= len(label) <= 60:
                    canonical.append({"label": label, "keywords": desc})

        K = self.cfg["n_topics"]
        if len(canonical) > K:
            canonical = canonical[:K]
        elif len(canonical) < K:
            if self.log:
                self.log.warning(f"LLM returned {len(canonical)} topics, expected {K}. Padding with fallbacks.")
            while len(canonical) < K:
                canonical.append({"label": f"topic_{len(canonical)+1}", "description": "Auto-generated fallback topic."})

        if self.log:
            self.log.info(f"Canonical taxonomy ({len(canonical)}): {[t['label'] for t in canonical]}")

        return canonical

    def _fallback_taxonomy(self) -> list[dict]:
        return [
            {"label": f"topic_{i+1}", "keywords": "[fallback]"}
            for i in range(self.cfg["n_topics"])
        ]
