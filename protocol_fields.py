

class ProtocolField:
    """
        Interface definition for a protocol field. 
    """
    def get_name(self):
        """Returns the name of the field"""
        pass
    
    def compute_struct_text(self):
        """Gives the text used to represent the field in a struct.pack or struct.unpack call"""
        pass

    def is_fixed_length(self):
        """Returns true if the field is fixed length and false otherwise"""
        return True

class ConstantLengthProtocolField(ProtocolField):
    """
        Defines a constant length protocol field.
        name: The name of the field.
        struct_text: the text used with struct to pack and unpack values for this field
        size: the size of the field in bytes
    """
    
    def __init__(self, name: str, struct_text: str, size: int):
        self.name = name
        self.struct_text = struct_text
        self.size = size

    def get_name(self):
        """Returns the name of the field"""
        return self.name
    
    def compute_struct_text(self):
        """Returns the text used to pack or unpack values of this field with the struct module"""
        return self.struct_text
    
    def get_size(self):
        """Returns the size of the field in bytes"""
        return self.size
    
class VariableLengthProtocolField(ProtocolField):
    """
        Defines a variable length protocol field. 
        name: the name of the field.
        create_struct_text: a function that computes the appropriate text for packing and unpacking values for the field
        as a function of the field size in bytes.
        max_size: the maximum size of the field in bytes
    """
    def __init__(self, name: str, create_struct_text, max_size: int = 1):
        self.name = name
        self.create_struct_text = create_struct_text
        self.max_size = max_size
    
    def get_name(self):
        """Returns the name of the field"""
        return self.name
    
    def compute_struct_text(self, size):
        """Returns the text for packing and unpacking values of the field is a function of the size"""
        return self.create_struct_text(size)
    
    def compute_struct_text_from_value(self, value):
        """Returns the text for packing and unpacking values of the field is a function of the value to pack or unpack"""
        return self.compute_struct_text(len(value))

    def get_max_size(self):
        """Returns the maximum size of the field in bytes"""
        return self.max_size
    
    def is_fixed_length(self):
        return False

def create_string_protocol_field(name, max_size_in_bytes):
    """
        Creates a protocol field for a string value as a function of the name and maximum size in bites
        name: the name of the field
        max_size_in_bytes: the maximum size of the field in bites
    """
    def create_struct_text(size):
        return str(size) + "s"
    field = VariableLengthProtocolField(name, create_struct_text, max_size_in_bytes)
    return field

def creates_single_byte_length_field_string_protocol_field(name):
    """
        Creates a protocol field with specified name for a variable length string where the length is contained in a single byte field
    """
    return create_string_protocol_field(name, 1)

def create_single_byte_nonnegative_integer_protocol_field(name):
    """
        Creates a protocol field for nonnegative integer values that fit in a single byte
    """
    field = ConstantLengthProtocolField(name, "B", 1)
    return field

def create_fixed_length_string_protocol_field(name, size):
    """Creates a fixed length string protocol field with specified name and size"""
    field = ConstantLengthProtocolField(name, str(size) + "s", size)
    return field
    