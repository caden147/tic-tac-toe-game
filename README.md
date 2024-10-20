# Tic-Tac-Toe Game 

This is a simple Tic-Tac-Toe game project that will be implemented using Python and sockets. 

## How to Play
The game is not implemented yet, but the client and server can send messages. Once the game has been implemented, you may play by doing the following:

1. **Start the server:** Run the `server.py` script, it requires the inputs (host) and (port). These command line arguments specify the host and port location that the server will be hosted at. Sample usages: 'python server.py localhost 65432' or 'python server.py 127.52.34.21 7745'.
2. **Connect clients:** Run the `client.py` script on any desired number of different machines or terminals. This also requires command line arguments (host) (port) (action) and an optional (value). The current supported action is 'help', with the associated 'gameplay', 'setup', or '' (nothing/blank) values.
3. **Play the game:** Players take turns entering their moves. The first player to get three in a row wins!

## Game Message Protocol Specification
The game message protocol defines the structure and format of messages exchanged between the server and clients.
* Message format: A struct-based format is used for message serialization and deserialization.
* Message structure: type_code: a single byte unique identifier for the message type at the start of every message. Field 1, Field 2, ...: Additional data fields specific to the message type. Variable length fields are preceded by a field specifying its length.

Abstract protocols (use to define concrete message protocols):
* Text message protocol: Contains a type code followed by a 2 byte field giving the length of the last field, which is a string.
* Username and password message protocol: Contains a type code followed by a 1 byte field giving the length of the next field. The next field is a string containing the username. The following field contains a one byte length of the following field, which is a string field containing the password. 

Message Protocols for Communicating From the Client to the Server:
* Help with no argument: type code 0. No other fields. Expected response: The base help response described below. 
* Help with argument: type code 1. A text message protocol with a string containing a specific topic to receive help on. The expected response is the help response with argument described below.
* Account creation request: type code 2. A username and password protocol for requesting the creation of an account. The expected response is a text message response describing if the account could be created or already existed. 
* Login request: Type code 3. A username and password protocol for logging in. The expected response is a text message response describing if login was successful. 

Message Protocols for Communicating From the Server to the Client:
* Base help response: a text message protocol with type code 0. The string contains a help message giving some information on how to communicate with the server.
* Help response with argument: a text message protocol with type code 1. If the request argument refers to a help topic supported by the server, the string contains help information on that topic. Otherwise, it reports that the received topic was not supported and additionally sends the base help text.
* Text message response: a text message protocol with type code 4 for giving miscellaneous updates to the client. 


Meeting notes:
- Have game moves by single bytes (1-9)

- Join game have one field: game ID

- Assign on the server side: player numbers as they connect

- Quit game: "q" (type code only)

- Sign in message (username/password)

- Account creation message (username/password)

- Single string chat protocol

- Game creation protocol (username with the person you want to be able to join) 

 
 

## Technologies Used
* Python
* Sockets

## Logging
Logs are utilized to document errors as well as client and server connect/disconnect events. These are located in the 'source' -> 'logs' directory under 'client.log' and 'server.log'. 

# Additional Resources
* [Link to Python Documentation](https://docs.python.org/3/)
* [Link to Sockets Documentation](https://docs.python.org/3/library/socket.html#example)
* [Link to Socket Tutorial](https://docs.python.org/3/howto/sockets.html)
* [Statement of Work](https://github.com/FireChickenProductivity/tic-tac-toe-game/blob/main/StatementOfWork.md)
