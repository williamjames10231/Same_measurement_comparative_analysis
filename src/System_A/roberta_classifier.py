import torch
import numpy as np
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

class RobertaClassifier:
    def __init__(
            self,
            data
    ) -> None:
        copy = data.copy()
        self.data = copy
        self.RoBERTa_model_name = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
        self.batch_size = 64
        self.max_len = 128

        #sentiment labels
        self.idx_neg, self.idx_neu, self.idx_pos = 0, 1, 2

    def roberta_model(
            self
    ):
        copy = self.data.copy()
        tokenizer = AutoTokenizer.from_pretrained(self.RoBERTa_model_name)
        model = AutoModelForSequenceClassification.from_pretrained(self.RoBERTa_model_name)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device).eval()
        print(f"Device: {device}")

        #copy = copy["text"].fillna("").astype(str).tolist()
        probs = self.predict_probs(
            copy["text"].tolist(),
            device,
            model,
            tokenizer
        )

        copy["prob_neg"] = probs[:, self.idx_neg]
        copy["prob_neu"] = probs[:, self.idx_neu]
        copy["prob_pos"] = probs[:, self.idx_pos]
        copy["polarity"] = copy["prob_pos"] - copy["prob_neg"]
        copy["confidence"] = probs.max(axis=1)

        copy["sentiment_pred"] = [self.robust_label(p) for p in probs]
        argmax = probs.argmax(axis=1)
        LABELS = {0: "Negative", 1: "Neutral", 2: "Positive"}
        copy["sentiment_argmax"] = [LABELS[i] for i in argmax]

        return copy

    @torch.no_grad
    def predict_probs(
            self,
            texts,
            device,
            model,
            tokenizer
    ):
        out = []
        n = len(texts)
        for i in range(0, n, self.batch_size):
            batch = [t if t.strip() else "[empty]" for t in texts[i:i + self.batch_size]]
            enc = tokenizer(batch, padding=True, truncation=True,
                            max_length=self.max_len, return_tensors="pt").to(device)
            p = torch.softmax(model(**enc).logits, dim=-1).cpu().numpy()
            out.append(p)
            if (i // self.batch_size) % 20 == 0:
                print(f"  {i + len(batch):>6}/{n}")
        return np.vstack(out)

    def robust_label(
            self,
            p,
            pos_t=0.60,
            neg_t=0.60,
    ):
        if p[self.idx_pos] >= pos_t: return "Positive"
        if p[self.idx_neg] >= neg_t: return "Negative"
        return "Neutral"

    def roberta_diagnostics(
            self,
            results
    ):
        copy = results
        print("\n" + "=" * 60)
        print("FULL RUN RESULTS")
        print("=" * 60)

        print("\n-- Softmax means --")
        print(f"  P(Neg) = {copy['prob_neg'].mean():.3f}")
        print(f"  P(Neu) = {copy['prob_neu'].mean():.3f}")
        print(f"  P(Pos) = {copy['prob_pos'].mean():.3f}")

        print("\n-- Argmax counts --")
        print(copy["sentiment_argmax"].value_counts())

        print("\n-- Robust label counts --")
        print(copy["sentiment_pred"].value_counts())

        print("\n-- Polarity describe --")
        print(copy["polarity"].describe().round(3))

        print("\n-- Confidence describe --")
        print(copy["confidence"].describe().round(3))
        print(f"  Fraction at 100% conf: {(copy['confidence'] > 0.999).mean():.1%}")

        print("\n-- Polarity by region --")
        print(copy.groupby("region")["polarity"].agg(["mean", "std", "count"]).round(3))

        print("\n-- Polarity by disaster event (top 10) --")
        print(copy.groupby("disaster_event")["polarity"]
              .agg(["mean", "count"])
              .sort_values("count", ascending=False)
              .head(10)
              .round(3))

        return copy