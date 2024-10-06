import protocol

HELP_MESSAGE_PROTOCOL_TYPE_CODE = 1
BASE_HELP_MESSAGE_PROTOCOL_TYPE_CODE = 0
CLIENT_PROTOCOL_MAP = protocol.ProtocolMap([
    protocol.create_text_message_protocol(BASE_HELP_MESSAGE_PROTOCOL_TYPE_CODE),
    protocol.create_text_message_protocol(HELP_MESSAGE_PROTOCOL_TYPE_CODE)
])

SERVER_PROTOCOL_MAP = protocol.ProtocolMap([
    protocol.create_fieldless_message_protocol(BASE_HELP_MESSAGE_PROTOCOL_TYPE_CODE),
    protocol.create_text_message_protocol(HELP_MESSAGE_PROTOCOL_TYPE_CODE)
])