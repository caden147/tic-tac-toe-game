import struct

class ProtocolField:
    def get_name(self):
        pass
    
    def compute_struct_text(self):
        """Gives the text used to represent the field in a struct.pack or struck.unpack call"""
        pass

class SimpleProtocolField(ProtocolField):
    def __init__(self, name: str, struct_text: str):
        self.name = name
        self.struct_text = struct_text

    def get_name(self):
        return self.name
    
    def compute_struct_text(self):
        return self.struct_text

class MessageProtocol:
    def __init__(self, type_code, fields):
        self.type_code = type_code
        self.fields = fields

    def compute_fields_string(self):
        text = ""
        for field in self.fields:
            text += field.compute_struct_text()
        return text

    def pack(self, *args):
        struck_format = ">" + self.compute_fields_string
        return struct.pack(struck_format, *args)

    def unpack(self, input_bytes):
        results = {}
        struck_format = "<" + self.compute_fields_string()
        values = struct.unpack(struck_format, input_bytes)
        for i in range(len(values)):
            name = self.fields[i].get_name()
            results[name] = values[i]
        return results


