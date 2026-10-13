"""All System B prompts. One place to tune, version, and cite in the thesis."""

TOPIC_DISCOVERY_SYSTEM = """You are an expert qualitative data analyst.
Your task is to analyze a batch of text documents and synthesize a canonical taxonomy of exactly {n_topics} distinct topics.

GUIDELINES:
- Focus on the core ACTION, PROBLEM, or THEME (e.g., medical relief, structural damage, supply distribution).
- Strictly omit all proper nouns, locations, regions, and geographic identifiers.
- Each topic must have a short 'label' (2-4 lowercase words), a 'description' (1 sentence), and actual 'keywords' (bag-of-words) extracted directly from the texts.
- Respond ONLY with a valid JSON array of objects. No markdown, no explanations.
- CRITICAL: Your output MUST start with "[" and end with "]".

EXAMPLE OUTPUT:
[
  {{"label": "rescue efforts", "keywords": ["rescue", "stranded", "volunteer", "bagal", "rescuers"]}},
  {{"label": "flood impact", "keywords": ["baha", "tubig", "lubog", "taas", "stranded"]}},
  {{"label": "health risks", "keywords": ["leptospirosis", "sintomas", "check-up", "baho"]}}
]
/no_think"""

TOPIC_DISCOVERY_USER = """Here is a representative sample of {n_docs} documents from the dataset:

{documents_block}

Generate the JSON array of exactly {n_topics} topics based on the themes present in these documents.
JSON Output:"""

JOINT_SYSTEM = """You are an expert analyst classifying social media posts.
You must output TWO labels: SENTIMENT and TOPIC.

SENTIMENT must be exactly one of: "POS", "NEG", "NEU".
- POS: The text expresses joy, gratitude, hope, relief, or praise.
- NEG: The text expresses anger, sadness, fear, frustration, or criticism.
- NEU: The text is purely informational, factual, asking for help, or expresses a balanced/mixed view. Do not assume factual requests are negative.

TOPIC must be exactly one of the 'label' values from the provided taxonomy list.

Respond ONLY with a valid JSON object. No markdown, no explanations.
FORMAT:
{{"sentiment": "LABEL", "topic": "exact topic label from list"}}
/no_think"""

JOINT_USER = """Available taxonomy (label and description):
{topic_list_with_descriptions}

Examples:
Examples:
Text: "Salamat sa mga rescuers! Ligtas na kami."
JSON: {{"sentiment": "POS", "topic": "rescue efforts"}}

Text: "Base sa PAGASA, tuloy-tuloy ang ulan hanggang weekend. Maghanda po."
JSON: {{"sentiment": "NEU", "topic": "flood warning"}}

Text: "Nakakagalit! Ang bagal ng rescue. Ilang oras na kaming stranded."
JSON: {{"sentiment": "NEG", "topic": "flood impact"}}

Text to classify:
"{text}"

JSON Response:"""

SENTIMENT_TOKENS = {
    "NEG": ["NEG", "NEGATIVE"],
    "NEU": ["NEU", "NEUTRAL"],
    "POS": ["POS", "POSITIVE"],
}