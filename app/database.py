from typing import Dict, List

_store: Dict[str, List[Dict[str, str]]] = {}


def init_db() -> None:
    _store.clear()


def insert_message(
    id: str,
    text: str,
    dialog_id: str,
    participant_index: int,
) -> None:
    did = str(dialog_id)
    if did not in _store:
        _store[did] = []
    _store[did].append({
        "text": text,
        "participant_index": participant_index,
    })


def select_messages_by_dialog(dialog_id: str) -> List[Dict[str, str]]:
    return _store.get(str(dialog_id), [])
