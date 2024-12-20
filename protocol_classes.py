from packing_utilities import *
from protocol_type_codes import *

class MessageProtocol:
    """
        Interface class for the MessageProtocol objects.
        A message protocol object defines how to convert between values associated with a message for the protocol
        and messages conforming to the protocol
    """
    def get_type_code(self):
        """Returns a type code integer defining which protocol it is"""
        pass

    def pack(self, *args):
        """Packs values into a message conforming to the protocol"""
        pass

    def is_fixed_length(self):
        """Returns true if the protocol is for fixed length messages and false otherwise"""
        return True
    
    def get_number_of_fields(self):
        """Returns the number of fields supported by the protocol"""
        pass

class TypeCodeOnlyMessageProtocol(MessageProtocol):
    """
        Defines a message protocol that only consists of a type code and no fields
        type_code: the type code for the protocol
    """
    def __init__(self, type_code):
        self.type_code = type_code
    
    def get_type_code(self):
        """Returns a type code integer defining which protocol it is"""
        return self.type_code

    def get_number_of_fields(self):
        """Returns the number of fields associated with the message protocol, in this case 0"""
        return 0

    def pack(self, *args):
        """Returns a message for the protocol containing only the type code"""
        return pack_type_code(self.type_code)

class FixedLengthMessageProtocol(MessageProtocol):
    """
        Defines a fixed length message protocol
        type_code: the type code for the protocol
        fields: the fields corresponding to the protocol
    """
    def __init__(self, type_code, fields):
        self.type_code = type_code
        self.fields = fields
        self.size = self._compute_size()

    def compute_fields_string(self):
        """Returns a string for packing and unpacking messages conforming to the protocol"""
        text = ">"
        for field in self.fields:
            text += field.compute_struct_text()
        return text

    def pack(self, *args):
        """Pacs values into a message conforming to the protocol"""
        args = [encode_value(value) for value in args]
        type_code_bytes = pack_type_code(self.type_code)
        values_bytes = struct.pack(self.compute_fields_string(), *args)
        return type_code_bytes + values_bytes

    def unpack(self, input_bytes):
        """
            Unpacks bytes corresponding to the protocol excluding the type code at the beginning into the contained values
            input_bytes: bytes for a message corresponding to the protocol excluding the type code
            returns: a dictionary mapping field names to the corresponding values
        """
        results = {}
        values = struct.unpack(self.compute_fields_string(), input_bytes)
        for i in range(len(values)):
            name = self.fields[i].get_name()
            results[name] = decode_value(values[i])
        return results

    def get_type_code(self):
        """Returns the type code associated with the protocol"""
        return self.type_code
    
    def _compute_size(self):
        """Returns the size in bytes of a message using the protocol"""
        size = 0
        for i in range(len(self.fields)):
            size += self.fields[i].get_size()
        return size
    
    def get_size(self):
        """Returns the size in bytes of a message using the protocol"""
        return self.size

    def get_number_of_fields(self):
        """Returns the number of fields corresponding to the protocol"""
        return len(self.fields)

class VariableLengthMessageProtocol(MessageProtocol):
    """
        Defines a variable length message protocol
        type_code: the type code for the protocol
        fields: the fields corresponding to the protocol
    """
    def __init__(self, type_code, fields):
        self.type_code = type_code
        self.fields = fields
    
    def get_type_code(self):
        """Returns the type code for the message protocol"""
        return self.type_code

    def is_fixed_length(self):
        """Returns false to indicate that this is not a fixed length message protocol"""
        return False
    
    def pack(self, *args):
        """Pacs values into a message conforming to the protocol"""
        args = [encode_value(value) for value in args]
        values_bytes = pack_type_code(self.type_code)
        for index, field in enumerate(self.fields):
            if field.is_fixed_length():
                field_bytes = struct.pack(">" + field.compute_struct_text(), args[index])
            else:
                field_bytes = struct.pack(">" + field.compute_struct_text_from_value(args[index]), args[index])
                size = len(field_bytes)
                size_bytes = struct.pack(">" + compute_format_representation_for_size(field.get_max_size()), size)
                field_bytes = size_bytes + field_bytes
            values_bytes += field_bytes
        return values_bytes
    
    def is_field_fixed_length(self, i):
        """Returns true if the field at index i is fixed length and false otherwise"""
        return self.fields[i].is_fixed_length()

    def is_last_field(self, i):
        """Returns true if the field at index i is the last and false otherwise"""
        return i == len(self.fields) - 1
    
    def compute_fixed_length_field_length(self, i):
        """Returns the field length for the field at index i assuming that it is fixed length"""
        field = self.fields[i]
        return field.get_size()
    
    def compute_variable_length_field_max_size(self, i):
        """Returns the maximum field length for the field at index i assuming that it is variable length"""
        field = self.fields[i]
        return field.get_max_size()
        
    def unpack_field_length(self, i, input_bytes, starting_index):
        """
            Unpacks a field length into an integer value
            i: the index of the corresponding field
            input_bytes: part of a message in bytes corresponding to the protocol
            starting_index: the start of the bytes in the message containing the field length
        """
        maximum_size = self.compute_variable_length_field_max_size(i)
        relevant_bytes = input_bytes[starting_index: starting_index + maximum_size]
        return struct.unpack(">" + compute_format_representation_for_size(maximum_size), relevant_bytes)[0]

    def unpack_variable_length_field(self, i, length, input_bytes, starting_index):
        """
            Unpacks a variable length field value
            i: the index for the field
            length: the length of the field value
            input_bytes: part of a message in bytes corresponding to the protocol
            starting_index: the start of the bytes in the message containing the value
        """
        field = self.fields[i]
        relevant_bytes = input_bytes[starting_index: starting_index + length]
        return decode_value(struct.unpack(">" + field.compute_struct_text(length), relevant_bytes)[0])
    
    def unpack_fixed_length_field(self, i, input_bytes, starting_index):
        """
            Unpacks bytes corresponding to a fixed length field
            i: the index for the field
            input_bytes: part of a message in bytes corresponding to the protocol
            starting_index: the start of the bytes in the message containing the value
        """
        field = self.fields[i]
        length = self.compute_fixed_length_field_length(i)
        relevant_bytes = input_bytes[starting_index: starting_index + length]
        return decode_value(struct.unpack(">" + field.compute_struct_text(), relevant_bytes)[0])
    
    def compute_field_name(self, i):
        """Returns the name of the field at the specified index"""
        field = self.fields[i]
        return field.get_name()
    
    def get_number_of_fields(self):
        """Returns the number of fields corresponding to the protocol"""
        return len(self.fields)