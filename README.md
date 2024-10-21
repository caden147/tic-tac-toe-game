# Tic-Tac-Toe Game 

This is a simple Tic-Tac-Toe game project that will be implemented using Python and sockets. 

## How to Play
The game is not implemented yet, but the client and server can send messages. Once the game has been implemented, you may play by doing the following:

1. **Start the server:** Run the `server.py` script, it requires the inputs (host) and (port). These command line arguments specify the host and port location that the server will be hosted at. Sample usages: 'python server.py localhost 65432' or 'python server.py 127.52.34.21 7745'.
2. **Connect clients:** Run the `client.py` script on any desired number of different machines or terminals. This also requires command line arguments (host) (port).
3. **Play the game:** Players take turns entering their moves. The first player to get three in a row wins!

Commands:
* **Register an account:** Upon successfully connecting to the server, you must register an account. To do this, type 'register' followed by your chosen username and password into the terminal, seperated by spaces.
* **Login to an account:** After you have created an account, you will need to login. Type 'login' followed by your registered username and password into the terminal, seperated by spaces.
* **Create a game:** To create a new game, type 'create' into the terminal followed by the username of your opponent.
* **Join a game:** To join someone else's game, type 'join' followed by your opponent's username.
* **Make a move:** To make a move, choose a space on the board and find it's corresponding coordinate. The columns are designated by 'a', 'b', or 'c'. The rows are '1', '2', or '3'. An example coordinate would be 'b3'. Type 'move' followed by the chosen coordinate into the terminal to make your move. You can only make a move on empty spaces.
* **Quit the game:** To quit a game, enter 'quit' into the terminal.
* **Help!:** If you'd like to see these commands during the game, type 'help', and the options will be displayed. Type 'help' followed by the command you would like more information about.

## Game Message Protocol Specification
The game message protocol defines the structure and format of messages exchanged between the server and clients.
* Message format: A struct-based format is used for message serialization and deserialization.
* Message structure: type_code: a single byte unique identifier for the message type at the start of every message. Field 1, Field 2, ...: Additional data fields specific to the message type. Variable length fields are preceded by a field specifying its length.

Abstract protocols (used to define concrete message protocols):
* Text message protocol: Contains a type code followed by a 2 byte field giving the length of the last field, which is a string.
* Username and password message protocol: Contains a type code followed by a 1 byte field giving the length of the next field. The next field is a string containing the username. The following field contains one byte giving the length of the following field, which is a string field containing the password. 
* Single byte message protocol: Contains a type code followed by a single byte that gets decoded as an unsigned integer. 
* Small text message protocol: Contains a type code, then a 1 byte field giving the length of the next field, and then a string field.
* Game board message protocol: Contains a type code and then a fixed length 9 byte string representing a tictactoe game board. Each character represents a position on the board. 

Message Protocols for Communicating From the Client to the Server:
* Help with no argument: type code 0. No other fields. Expected response: The base help response described below. 
* Help with argument: type code 1. A text message protocol with a string containing a specific topic to receive help on. The expected response is the help response with argument described below.
* Account creation request: type code 2. A username and password protocol for requesting the creation of an account. The expected response is a text message response describing if the account could be created or already existed. 
* Login request: Type code 3. A username and password protocol for logging in. The expected response is a text message response describing if login was successful. 
* Game update request: Type code 5. A single byte message protocol describing a move performed by the user. The number represents the tile to perform the move on. The expected response is either a game update response giving the new board state or a text message response explaining that the move was not permitted.
* Join game request: a small text message protocol with type code 6 and the string giving the name of the other player in the game to join. Only one game is permitted between 2 players at a time. The expected response is a game update response giving the state of the board if successful and a text message response explaining what went wrong if unsuccessful.
* Quit game request: consists only of type code 7.
* Chat message protocol: a text message protocol with type code 8 and the string containing a chat message to send to the other person playing the active game. There is no expected response message.
* Game creation protocol: a small text message protocol with type code 9 and the string containing the name of the player to invite to the game. The expected response is a text message explaining if the game creation was successful. 

Message Protocols for Communicating From the Server to the Client:
* Base help response: a text message protocol with type code 0. The string contains a help message giving some information on how to communicate with the server.
* Help response with argument: a text message protocol with type code 1. If the request argument refers to a help topic supported by the server, the string contains help information on that topic. Otherwise, it reports that the received topic was not supported and additionally sends the base help text.
* Text message response: a text message protocol with type code 4 for giving miscellaneous updates to the client. 
* Game update response: a game board message protocol with type code 5. This gives the board for the active game and is sent when a player joins a game or after a move is made.
* Chat message response: a text message protocol with type code 9 sending a text message to the desired recipient. 


## Technologies Used
* Python
* Sockets

## Logging
Logs are utilized to document errors as well as client and server connect/disconnect events. These are located in the 'logs' directory under 'client.log' and 'server.log'. 

# Additional Resources
* [Link to Python Documentation](https://docs.python.org/3/)
* [Link to Sockets Documentation](https://docs.python.org/3/library/socket.html#example)
* [Link to Socket Tutorial](https://docs.python.org/3/howto/sockets.html)
* [Statement of Work](https://github.com/FireChickenProductivity/tic-tac-toe-game/blob/main/StatementOfWork.md)
