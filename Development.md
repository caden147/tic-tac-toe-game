# How to Define a Message Protocol
1. Define a unique numeric type code for the protocol and put this in protocol_definitions.py.

2. Check to see if any of the abstract protocol creation functions defined at the bottom of Protocol meet your requirements. These create a protocol with already defined fields given the type code. If none of them meet your needs, go to step 3. Otherwise, go to step 6.

3. Define any needed fields that meet your requirements. See the section on defining fields for details.

4. Create your message protocol object by using the protocol.py create_protocol function with the type code and any needed fields as arguments. 

5. If the protocol requires any fields, create an abstract protocol creation function for the fields to make future development easier.

6. Add the protocol to the relevant protocol map in protocol_definitions.py. 


# How to Define a Message Protocol Field
1. See if a suitable message protocol field creation function exists at the bottom of protocol_fields.py. If one of the meets your needs, call it with the required parameters and go to step 5. Otherwise, go to step 2.

2. Decide if the field is going to be fixed length or variable length. If it is going to be fixed length, go to step 3. Otherwise, go to step 4.

3. Create a ConstantLengthProtocolField using the name of the field, the struct text for packing and unpacking the data (See [Format Characters Documentation](https://docs.python.org/3/library/struct.html#format-characters) for details). Go to step 5.

4. Create a VariableLengthProtocolField. Provide the name of the field, a function that creates struct text for packing the object using the result of calling len on the object as an argument, and the size of the length field that comes before your variable length field in bytes. 

5. Create a function for creating fields with the desired properties to make future work easier. The function should take the desired name for the field and, if the field is variable length, the size of the length field in bytes.


