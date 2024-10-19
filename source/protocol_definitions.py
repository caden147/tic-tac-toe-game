import protocol

HELP_MESSAGE_PROTOCOL_TYPE_CODE = 1
BASE_HELP_MESSAGE_PROTOCOL_TYPE_CODE = 0
ACCOUNT_CREATION_PROTOCOL_TYPE_CODE = 2
SIGN_IN_PROTOCOL_TYPE_CODE = 3
TEXT_MESSAGE_PROTOCOL = 4
#For communicating with the client
CLIENT_PROTOCOL_MAP = protocol.ProtocolMap([
    protocol.create_text_message_protocol(BASE_HELP_MESSAGE_PROTOCOL_TYPE_CODE),
    protocol.create_text_message_protocol(HELP_MESSAGE_PROTOCOL_TYPE_CODE)
    protocol.create_text_message_protocol(TEXT_MESSAGE_PROTOCOL)
])

#For communicating with the server
SERVER_PROTOCOL_MAP = protocol.ProtocolMap([
    protocol.create_protocol(BASE_HELP_MESSAGE_PROTOCOL_TYPE_CODE),
    protocol.create_text_message_protocol(HELP_MESSAGE_PROTOCOL_TYPE_CODE),
    protocol.create_username_and_password_message_protocol(ACCOUNT_CREATION_PROTOCOL_TYPE_CODE),
    protocol.create_username_and_password_message_protocol(SIGN_IN_PROTOCOL_TYPE_CODE)
])