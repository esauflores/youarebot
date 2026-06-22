import logging

from transformers import pipeline

from .config import CANDIDATE_LABELS, HYPOTHESIS_TEMPLATE, MODEL_NAME

logger = logging.getLogger(__name__)
_classifier = None


def load_model():
    global _classifier
    if _classifier is None:
        logger.info("Loading zero-shot-classification pipeline (%s)...", MODEL_NAME)
        logger.info("First load downloads ~1.7GB from HuggingFace — may take 2-5 min")
        _classifier = pipeline(
            "zero-shot-classification",
            model=MODEL_NAME,
            device=-1,
            model_kwargs={"attn_implementation": "eager"},
        )
    return _classifier


def format_conversation(messages: list[dict]) -> str:
    return "\n".join(f"{msg['participant_index']}: {msg['text']}" for msg in messages)


def classify_text(messages: list[dict]) -> float:
    classifier = load_model()
    conversation_text = format_conversation(messages)

    prompt = (
        "Analyze this conversation between participant 0 and participant 1.\n"
        "Bot indicators: overly perfect grammar, generic agreeable responses, "
        "no typos, no casual filler words (uh, hmm, like, well), "
        "no contractions, unnaturally consistent tone, "
        "no personality, no hedging or uncertainty, "
        "avoiding opinions, never asking questions back.\n"
        "Human indicators: typos, casual tone, filler words, contractions, "
        "opinions, emotional reactions, short simple replies, "
        "topic shifts, imperfect grammar, slang.\n\n"
        f"{conversation_text}"
    )

    result = classifier(
        prompt,
        candidate_labels=CANDIDATE_LABELS,
        hypothesis_template=HYPOTHESIS_TEMPLATE,
    )

    bot_index = result["labels"].index(CANDIDATE_LABELS[0])
    probability = float(result["scores"][bot_index])
    return max(0.0, min(1.0, probability))
