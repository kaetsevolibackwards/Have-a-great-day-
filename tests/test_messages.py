from core.generator import generate_message
from core.messages import Message


def test_generate_message_roundtrip():
    msg = generate_message('fact')
    assert isinstance(msg, Message)
    raw = msg.to_json()
    msg2 = Message.from_json(raw)
    assert msg.id == msg2.id
    assert msg.message == msg2.message
