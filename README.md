# Tic-Tac-Toe Game 

This is a simple Tic-Tac-Toe game project that will be implemented using Python and sockets. 

## How to Play
The game is not implemented yet, but the client and server can send messages. Once the game has been implemented, you may play by doing the following:

1. **Start the server:** Run the `server.py` script, it requires the inputs (host) and (port). These command line arguments specify the host and port location that the server will be hosted at. Sample usages: 'python server.py localhost 65432' or 'python server.py 127.52.34.21 7745'.
2. **Connect clients:** Run the `client.py` script on any desired number of different machines or terminals. This also requires command line arguments (host) (port) (action) and an optional (value). The current supported action is 'help', with the associated 'gameplay', 'setup', or '' (nothing/blank) values.
3. **Play the game:** Players take turns entering their moves. The first player to get three in a row wins!

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
    
