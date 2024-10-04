import struct

TYPE_CODE_SIZE = 1
def pack_type_code(type_code: int):
    return struct.pack(">B", type_code)

def unpack_type_code_from_message(message):
    relevant_bytes = message[:TYPE_CODE_SIZE]
    type_code = struct.unpack(">B", relevant_bytes)[0]
    return type_code

def compute_message_after_type_code(message):
    return message[TYPE_CODE_SIZE:]


class ProtocolField:
    def get_name(self):
        pass
    
    def compute_struct_text(self):
        """Gives the text used to represent the field in a struct.pack or struck.unpack call"""
        pass

    def get_size(self):
        """Returns the size in bytes of the field"""
        pass

class SimpleProtocolField(ProtocolField):
    def __init__(self, name: str, struct_text: str, size: int):
        self.name = name
        self.struct_text = struct_text
        self.size = size

    def get_name(self):
        return self.name
    
    def compute_struct_text(self):
        return self.struct_text
    
    def get_size(self):
        return self.size

class MessageProtocol:
    def __init__(self, type_code, fields):
        self.type_code = type_code
        self.fields = fields

    def compute_fields_string(self):
        text = ">"
        for field in self.fields:
            text += field.compute_struct_text()
        return text

    def pack(self, *args):
        type_code_bytes = pack_type_code(self.type_code)
        values_bytes = struct.pack(self.compute_fields_string(), *args)
        return type_code_bytes + values_bytes

    def unpack(self, input_bytes):
        results = {}
        values = struct.unpack(self.compute_fields_string(), input_bytes)
        for i in range(len(values)):
            name = self.fields[i].get_name()
            results[name] = values[i]
        return results

    def get_type_code(self):
        return self.type_code
    
    def compute_size(self):
        """Returns the size in bytes of a message using the protocol"""
        size = 0
        for i in range(len(self.fields)):
            size += self.fields[i].get_size()
        return size

class ProtocolMap:
    """Maps between type codes and protocols"""
    def __init__(self, protocols):
        """protocols: an iterable of MessageProtocols"""
        self.map = {}
        for protocol in protocols:
            self.map[protocol.get_type_code()] = protocol
        
    def get_protocol_with_type_code(self, code: int):
        """Returns the protocol with the associated type code"""
        return self.map[code]
    
    def has_protocol_with_type_code(self, code: int):
        """Returns true if the map has a protocol with the specified type code and false otherwise"""
        return code in self.map
    
