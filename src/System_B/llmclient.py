import json
import numpy as np
from llama_cpp import Llama
import re


def extract_json_array(text: str) -> list | None:
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    if text.startswith("{"):
        text = "[" + text
    if text.endswith("}") or text.endswith("},"):
        text = text.rstrip(",") + "]"
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    return None

class LLMClient:
    def __init__(
        self,
        cfg : dict,
        logger=None
    ) -> None:
        self.cfg = cfg["llm"]
        self.log = logger
        self.model_path = self.cfg.get("gguf_filename")

        self.n_gpu_layers = self.cfg.get("n_gpu_layers", -1)
        self.n_ctx = self.cfg.get("n_ctx", 32768)

        if logger:
            logger.info(f"Loading {self.model_path} via llama.cpp")

        self.model = Llama(
            model_path=self.model_path,
            n_gpu_layers=self.n_gpu_layers,
            n_ctx=self.n_ctx,
            logits_all=True,
            verbose=True,
            n_threads=2,
        )

        if logger:
            logger.info("Model successfully loaded into memory.")

    def generate(
        self,
        system : str,
        user : str,
        max_new_tokens: int = 1024,
        force_json=True
    ) -> str:
       messages = [
           {"role": "system", "content": system},
           {"role": "user", "content": user},
       ]

       response = self.model.create_chat_completion(
           messages=messages,
           max_tokens=max_new_tokens,
           temperature=self.cfg.get("temperature"),
           top_p=self.cfg.get("top_p"),
       )

       # Build generation kwargs
       #gen_kwargs = {
       #    "messages": messages,
       #    "max_tokens": max_new_tokens,
       #    "temperature": self.cfg.get("temperature"),
       #    "top_p": self.cfg.get("top_p"),
       #}

       # THE MAGIC BULLET: Force JSON output at the logits level
       #if force_json:
       #    gen_kwargs["response_format"] = {"type": "json_object"}

       #response = self.model.create_chat_completion(**gen_kwargs)

       text = response["choices"][0]["message"]["content"]
       start_idx = text.find('{')
       end_idx = text.rfind('}') + 1
       json_array_string = text[start_idx:end_idx]

       return json_array_string if json_array_string is not None else ""

    def classify_with_logprobs(self, system: str, user: str, token_map: dict[str, list[str]]) -> tuple[
        str, dict[str, float], str]:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        prompt_str = self._chat_prompt(system, user)

        input_tokens = self.model.tokenize(prompt_str.encode("utf-8"))
        self.model.eval(input_tokens)

        logits = np.array(self.model._scores[-1])
        logits -= np.max(logits)  # Stable softmax
        logprobs = logits - np.log(np.sum(np.exp(logits)))

        label_scores = {}
        for label, variants in token_map.items():
            best = -float("inf")
            for v in variants:
                ids = self.model.tokenize(v.encode("utf-8"), add_bos=False)
                if not ids: continue
                lp = logprobs[ids[0]]
                if lp > best: best = lp
            label_scores[label] = best

        vals = np.array(list(label_scores.values()))
        vals -= np.max(vals)
        probs = np.exp(vals)
        probs = probs / probs.sum()
        label_probs = dict(zip(label_scores.keys(), probs.tolist()))


        gen_res = self.model.create_chat_completion(
            messages=messages,
            max_tokens=150,
            temperature=self.cfg.get("temperature", 0.0),
            top_p=self.cfg.get("top_p", 0.95),
        )

        text = gen_res["choices"][0]["message"]["content"] if gen_res.get("choices") else ""
        top = max(label_probs, key=label_probs.get)

        return top, label_probs, text.strip()

    def _chat_prompt(
            self,
            system: str,
            user: str
    ) -> str:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        if hasattr(self.model, "metadata") and "tokenizer.chat_template" in self.model.metadata:
            try:
                return self.model.chat_format.get_format()(
                    messages=messages,
                    enable_thinking=False
                ).prompt
            except Exception:
                pass

            # Clean fallback format
        return f"<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n"