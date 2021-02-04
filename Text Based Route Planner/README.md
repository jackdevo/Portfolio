# Text-Based Route Planner

![](https://img.shields.io/github/followers/jackdevonshire?style=social)

A simple Python application that utilizes TransportAPI to provide text-based navigation

### Disclaimer
----

As of testing on 12/12/2020 this program no longer works. I assume this is due to a TransportAPI update since the initial
writing of the program. I may update it in the future, but for now, the code serves its purpose as a portfolio piece.

### Usage
----

Route Planner takes 2 arguments, the current address, and the target address.
e.g >> routePlanner.py "My House A12 3BC" "My Other House C32 1BC"

### Limitations
----

This project was one of the first things I created when I learned about API's (aka a long time ago),
so its limitations are pretty endless...
1. Doesn't work on mobile as its a python script
2. Doesn't interact with any hardware based GPS module to get the current location
3. Text-Based = Incredibly Dangerous
4. No UI at all
5. And So On...

### Credits
----

Everyting in this script was created by myself.

Credits to developers of the following requirements:
- TransportAPI
- geopy
