# How to Define a Message Protocol
1. Define a unique numeric type code for the protocol and put this in protocol_definitions.py.

2. Check to see if any of the abstract protocol creation functions defined at the bottom of Protocol meet your requirements. These create a protocol with already defined fields given the type code. If none of them meet your needs, go to step 3. Otherwise, go to step 6.

3. Define any needed fields that meet your requirements. See the section on defining fields for details.

4. Create your message protocol object by using the protocol.py create_protocol function with the type code and any needed fields as arguments. 

5. If the protocol requires any fields, create an abstract protocol creation function for the fields to make future development easier.

6. Add the protocol to the relevant protocol map in protocol_definitions.py. 


# How to Define a Message Protocol Field
