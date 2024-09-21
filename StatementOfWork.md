# Statement of Work (SOW) Template for Socket Programming Project
## Project Title:
Tacs Free Tic-Tac-Toe

## Team:
Samuel Dianda, Caden Clark, Anton Vulman

## Project Objective:
The goal of the project is to implement server-client communication allowing multiple clients to connect to a server to play games of Tic-Tac-Toe synchronously, which will demonstrate fundamental concepts of networking and socket programming.

## Scope:
### Inclusions:
- Client-server architecture with multiple client connections
- Messaging protocol for client-server communication
- Error handling for network failures, invalid input, and unexpected game states
- Proper Tic-Tac-Toe game functionality
- Command line interface (CLI) based user interface
- Encrypt messages/communications

### Exclusions:
- Web based user interface
- Chat functionality
- Special game modes
- Ranked/competitive system

## Deliverables:
- Working Python script for both the client and the server
- Game board is visible to the user via CLI
- Documentation for how to use client/server
- Thorough README.md and clear yet effective code comments

## Timeline:
### Key Milestones:
- Sprint 0: Form teams, Setup Tools, Submit SOW (Sept 08-Sept 22)
- Sprint 1: Socket Programming, TCP Client and Server (Sept 22-Oct 06)
- Sprint 2: Develop Game Message Protocol, Manage Client connections (Oct 06-Oct 20)
- Sprint 3: Implement Multiplayer functionality, Synchronize state across clients. (Oct 20-Nov 03)
- Sprint 4:  Implement Game play, Game State (Nov 03-Nov 17)
- Sprint 5: Implement Error Handling and Testing (Nov 17-Dec 6)


### Task Breakdown:
- Command Line Argument Parsing (3 hours)
- Log Connection and Disconnection Events (5 hours)
- Server Socket Programming (1-4 days)
- Client Socket Programming (1-4 days)
- Create Protocol System (7 days)
- Game Message Protocol (7 days)
- Game Management Protocol (7 days)
- Synchronize State (2 days)
- Handle Network Latency (4 days)
- Player Identifiers (4 hours)
- Track Player Identity and Data in Database/Login System (8 hours)
- Account Security (3 days)
- Define Win Conditions (2 hours)
- Notify Handle End Game (5 hours)
- Notify Player of Game Outcome (6 hours)
- Game logic implementation (6 hours)
- CLI-based user interface development (6 hours)
- Error handling, logging and code implementation corrections (5 hours)
- Handle Network Errors (3 days)
- Test Edge Cases (4 days)
- Testing/debugging (ongoing)

## Technical Requirements:
### Hardware:
- A server for hosting the server program
- Computer keyboards or alternate input devices for controlling the command line interface programs
- Computers for running the client program
- Internet connected routers for sending internet packets for the client-server communications

### Software:
- Git
- GitHub
- Web browsers for accessing GitHub
- Talon Voice (for coding by voice)
- Cursorless (for efficient code editing by voice)
- The Python Programming Language
- The python socket library (part of the standard python library)
- Linux, Windows, and Mac operating systems for testing

## Assumptions:
- We assume that we will be able to obtain the hardware and software specified in the above technical requirements
- We assume that we will have sufficient internet access and bandwidth to collaborate on the project and test it remotely
- We assume that we will have the ability to access project details/information, as well as access to Office Hours with TA’s for extra support as necessary
- We assume that all members have knowledge of basic networking and Python programming.

## Roles and Responsibilities:
- Security Risk Manager/Tester: Anton
- Identify security risks and suggest solutions or design decisions
- Design Managers: Samuel, Caden
- Identify where design patterns would be useful and apply them
- Refactoring Expert: Samuel
- Is primarily responsible for refactoring tasks
- Developers: Anton, Caden, Samuel
- Database Manager: Samuel
- Testers:
    - Windows Testers: Anton, Caden
    - Mac Tester: Samuel
    - Linux Testers: Anton, Caden, Samuel

## Communication Plan:
- Microsoft Teams for meetings and text communications
- GitHub issues for tracking and discussing specific tasks
- We will check in with each other at least once a week for the sake of forming and revising plans
- We plan on meeting every Monday at 7PM as a standard meeting time unless we agree there is nothing that we need to discuss. This convention prevents us from needing to negotiate/plan a meeting if something requires discussion

## Additional Notes:
- The roles and responsibilities only define who is responsible for making sure the associated activities are completed. Team members may contribute to roles outside of their direct responsibilities
- We will all jointly self-manage the project based on the collaboration style taught in cs314
- This document will be continuously updated throughout the project based on changing expectations and unexpected roadblocks
