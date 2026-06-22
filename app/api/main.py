import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.api.classify import classify_text, load_model
from app.api.llm_client import get_llm_reply
from app.core.logging import app_logger
from app.database import init_db, insert_message, select_messages_by_dialog
from app.models import GetMessageRequestModel, GetMessageResponseModel, IncomingMessage, Prediction


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    load_model()
    yield


app = FastAPI(
    title="YouAreBot - LLM + Classifier",
    description="LLM-powered bot with zero-shot classification",
    lifespan=lifespan,
)


@app.post("/get_message", response_model=GetMessageResponseModel)
async def get_message(body: GetMessageRequestModel):
    app_logger.info(f"Received message dialog_id: {body.dialog_id}, last_msg_id: {body.last_message_id}")

    insert_message(
        id=body.last_message_id or uuid.uuid4(),
        text=body.last_msg_text,
        dialog_id=body.dialog_id,
        participant_index=0,
    )

    history = select_messages_by_dialog(body.dialog_id)
    reply = get_llm_reply(history)

    reply_id = uuid.uuid4()
    insert_message(
        id=reply_id,
        text=reply,
        dialog_id=body.dialog_id,
        participant_index=1,
    )

    full_dialog = select_messages_by_dialog(body.dialog_id)
    try:
        bot_prob = classify_text(full_dialog)
    except Exception:
        app_logger.exception("Classification failed")
        bot_prob = None

    return GetMessageResponseModel(
        new_msg_text=reply,
        dialog_id=body.dialog_id,
        is_bot_probability=bot_prob,
    )


@app.post("/predict", response_model=Prediction)
def predict(msg: IncomingMessage) -> Prediction:
    insert_message(
        id=msg.id,
        text=msg.text,
        dialog_id=msg.dialog_id,
        participant_index=msg.participant_index,
    )

    conversation_text = select_messages_by_dialog(msg.dialog_id)
    if not conversation_text:
        raise HTTPException(
            status_code=404,
            detail="No messages found for this dialog_id",
        )

    is_bot_probability = classify_text(conversation_text)
    prediction_id = uuid.uuid4()

    return Prediction(
        id=prediction_id,
        message_id=msg.id,
        dialog_id=msg.dialog_id,
        participant_index=msg.participant_index,
        is_bot_probability=is_bot_probability,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
