# Tic-Tac-Toe Game 

This is a simple Tic-Tac-Toe game project that is implemented using Python and sockets. 

## How to Play
You can play the game by doing the following:

1. **Start the server:** Run the `server.py` script: it requires the input -p (port number). The host can optionally be specified with -i (IP address). If unspecified, the server is started at address 0.0.0.0. These command line arguments specify the host and port location that the server will be hosted at. Sample usages: 'python server.py -p 65432' or 'python server.py -p 7745 -i localhost'.
2. **Connect clients:** Run the `client.py` script on any desired number of different machines or terminals. This also requires command line arguments -i (host) -p (port).
3. **Play the game:** Players take turns entering their moves. The first player to get three in a row wins!

Use the register command documented below to create an account if you do not have one. Use the login command to login. You can start a game with the create command. You can join a game that you created or got invited to with the join command. After joining, you make moves with the move command.

Commands:
* **Register an account:** Upon successfully connecting to the server, you must register an account. To do this, type 'register' followed by your chosen username and password into the terminal, seperated by spaces.
* **Login to an account:** After you have created an account, you will need to login. Type 'login' followed by your registered username and password into the terminal, seperated by spaces.
* **Create a game:** To create a new game, type 'create' into the terminal followed by the username of your opponent.
* **Join a game:** To join a game, type 'join' followed by your opponent's username. A game creator must join their game to make moves in it. 
* **Make a move:** To make a move, choose a space on the board and find it's corresponding coordinate. The rows are designated by 'a', 'b', or 'c'. The columns are '1', '2', or '3'. An example coordinate would be 'b3'. Type 'move' followed by the chosen coordinate into the terminal to make your move. You can only make a move on empty spaces.
* **Quit the game:** To quit a game, enter 'quit' into the terminal.
* **Help!:** If you'd like to see these commands during the game, type 'help', and the options will be displayed. Type 'help' followed by the command you would like more information about.
* **Exiting the program:** To exit the program, type 'exit'.

Reconnection:

When the client program detects a problem with the server connection, it tries to reconnect with the server. The amount of time that it waits after each subsequent reconnection attempt increases until it reaches the maximum waiting time of 30 seconds. If the client program receives a message from the server, it resets the waiting time back to the minimum. The user currently has to log in again after the reconnection.

## Security/Risk Evaluation
- Passwords are stored in plaintext, while they should be stored as secure hashes.
- There is a lack of input validation, specifically for the functions used to construct database queries which can lead to injection attacks.
- No encryption is present, from the connection to the communications.
- The database doesn't have set permissions and rule of least privilege is not employed, meaning unauthorized access can be gained.
- There is no password requirement or password validation parameters, meaning an account password may easily be bruteforced.

## Roadmap
In the future, this game could be improved with a web-based UI and encryption. While the commandline interface works well, web-based games are a lot more user-friendly. This could also allow users to view their profile information more easily and keep track of their games. We could also implement a search function to find active users in case someone doesn't have a specific opponent in mind for their game.
As for encryption, none of the user data is currently encrypted. We could hash passwords and encrypt the traffic between the client and server.

## Retrospective
Overall, the technical aspect of this project went very well. The finished game works great with minimal bugs. When bugs were found, they were always quickly addressed and resolved.

Throughout the project, our biggest challenge was communication. The expectations and plans for the project were unclear, so it caused some tension between the team. We were also not very organized with our task planning. If we had more clear expectations and tasks for each sprint, we could've had a lot fewer miscommunications.

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
* Fixed length string message protocol: Contains a type code and then a fixed length string.
* Single character message protocol: Contains a type code followed by single character in a single byte. 
* Single username and single character message protocol: Contains a type code and then a variable length string with its length determined by a single byte field. The last field is a single byte character.

Message Protocols for Communicating From the Client to the Server:
* Help with no argument: type code 0. No other fields. Expected response: The base help response described below. 
* Help with argument: type code 1. A text message protocol with a string containing a specific topic to receive help on. The expected response is the help response with argument described below.
* Account creation request: type code 2. A username and password protocol for requesting the creation of an account. The expected response is a text message response describing if the account could be created or already existed. 
* Login request: Type code 3. A username and password protocol for logging in. The expected response is a text message response describing if login was successful. 
* Game update request: Type code 5. A single byte message protocol describing a move performed by the user. The number represents the tile to perform the move on. The expected response is either a game update response giving the new board state or a text message response explaining that the move was not permitted. If the move ends the game, a game ending message response is expected. 
* Join game request: a small text message protocol with type code 6 and the string giving the name of the other player in the game to join. Only one game is permitted between 2 players at a time. The expected response is a game piece update message describing the piece controlled by the player followed by a game update response giving the state of the board if successful and a text message response explaining what went wrong if unsuccessful.
* Quit game request: consists only of type code 7.
* Chat message protocol: a text message protocol with type code 8 and the string containing a chat message to send to the other person playing the active game. There is no expected response message.
* Game creation protocol: a small text message protocol with type code 9 and the string containing the name of the player to invite to the game. The expected response is a text message explaining if the game creation was successful. 

Message Protocols for Communicating From the Server to the Client:
* Base help response: a text message protocol with type code 0. The string contains a help message giving some information on how to communicate with the server.
* Help response with argument: a text message protocol with type code 1. If the request argument refers to a help topic supported by the server, the string contains help information on that topic. Otherwise, it reports that the received topic was not supported and additionally sends the base help text.
* Text message response: a text message protocol with type code 4 for giving miscellaneous updates to the client. 
* Game update response: a game board message protocol with type code 5. This gives the board for the active game and is sent when a player joins a game or after a move is made.
* Chat message response: a text message protocol with type code 9 sending a text message to the desired recipient. 
* Game ending protocol: a single username and single character message protocol with type code 11. This is sent at the end of a game. The single character at the end describes if the game ended in a win, loss, or tie for the notified player. The username contains the name of the opponent to allow distinguishing between games.
* Game piece protocol: a single character message protocol with type code 10 containing the game piece belonging to the messaged player. This is sent when a player joins a game.

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

# Mock Socket Testing Framework
Interactions between the server and clients can be tested with a custom unit testing framework that simulates sockets and selectors. See mock_socket.py and testing_utilities.py for the code. Tests written in this framework can be seen in test_communication.py. 

Sample test:

```python
        expected_message = Message(0, {'text': help_messages[""]})
        testcase = TestCase()
        testcase.create_client("Bob")
        testcase.buffer_client_command("Bob", "help")
        testcase.buffer_client_command("Bob", 1)
        testcase.run()
        output = testcase.get_output("Bob")
        print('output', output)
        testcase.assert_received_values_match_log([expected_message], 'Bob')
        testcase.assert_values_match_output([ContainsMatcher("Help")], 'Bob')
```

The expected message is the message expected from the server to the client. A test case object is created for the test. A client named "Bob" is created inside this test case. It buffers the commands "help" and 1. This means that this will stimulate Bob running the help command and then wait until the total number of received messages at this simulated client is at least 1 before proceeding. This prevents the client from terminating before it has finished receiving messages. A number is used here to decide how many messages must be received before proceeding. A timeout throws an exception if this takes too long. This is useful for making the simulated client receive responses from prior messages or messages that result from other simulated clients before executing the following instructions.

The test case is ran with the run method. The output obtained is the output to the client's simulated terminal. The first assertion statement asserts that the received messages are as expected. The second assertion asserts that that the simulated client terminal output consists of a single message containing the text "Help" somewhere inside it. 

The object SkipItem() can be used in one of the assertion lists to mean that whatever is in that position can be ignored.

The following test uses should_perform_automatic_login=True to specify that clients should be automatically logged into the server. The corresponding identities are generated automatically if nonexistent. The clients wait for the login responses before performing any actions. The login response is skipped with a SkipItem() in the below test. Note that the total number of messages received for waiting must include the initial login response even with automatic login. 

```python
        testcase = TestCase(should_perform_automatic_login=True)
        testcase.create_client("Bob")
        testcase.create_client("Alice")
        testcase.buffer_client_commands("Bob", ["create Alice", 2, "join Alice", 4, 'quit', 5])
        testcase.buffer_client_commands("Alice", [4, 'join Bob', 6])
        testcase.run()
        expected_alice_messages = [
            SkipItem(),
            create_text_message("Bob invited you to a game!"),
            create_text_message("Bob has joined your game!"),
            create_text_message("Bob has left your game!"),
            PLAYING_O_MESSAGE,
            EMPTY_GAME_BOARD_MESSAGE,
        ]
        testcase.assert_received_values_match_log(expected_alice_messages, "Alice")
```

The testing_utilities.py WaitingCommand objects can be used to wait for other conditions before letting a simulated client continue. 
