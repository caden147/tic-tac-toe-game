import struct

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
        return struct.pack(self.compute_fields_string(), *args)

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
        for i in range(len(values)):
            size += self.fields[i].get_size()
        return size

