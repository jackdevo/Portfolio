# Text Based Route Planner

![](https://img.shields.io/github/followers/jackdevo?style=social)

An addon script created for pyTson. pyTson is an addon that enables users to create and utilise Python scripts within the Teamspeak 3 Client
(A VOIP solution widely used by gaming communities).

This script utilises various API's, including Cleverbot for AI functionality and Pushover for IOS notifications.


### Context
----

A lot of the code in this script will not make sense, as it is heavily based around functions required for an online Arma 3 Altis Life community.

Arma 3 is a game engine, and Altis Life is a type of gamemode where there are different groups of people (Police, Civillian, Rebel). On
the particular community this script was made for, I was the chief of police recruitment and as such was regularly spammed with messages.
This script was created to aid me in responding to people who had compelx questions, whilst automatically giving basic information to new
candidates - with the AI and other features on the side for a novelty factor.

Please get in touch for more information, if you want to learn more.

### Disclaimer
----

pyTson was discontinued quite a few Teamspeak versions back, hence this addon no longer works.

### Installation
----

https://pypi.org/project/cleverbot.py/
https://stackoverflow.com/questions/29817447/how-to-run-pip-commands-from-cmd/29817514
1. Follow instructions on pyTson website
2. Drag tsResponder.py and ignore.tst to pyTson scripts folder, and place in a new sub directory /tsResponder

To install pyTson packages:
1. cd \TeamspeakLocation\config\plugins\pyTson
2. python -m pip install packageName

### Functions
----

This script (when it worked) was able to:

1. Detect when people where asking community specific questions (such as a faction handbook) and provide the relevant link or information
2. Allow people to be added/removed from an ignore list incase they didn't want to receive automated responses
3. Allow the user to set availability. E.g if set to unavailable, any messages would be replied to with a not avaialble notification
4. Stop all AI responses when a user manually replied to an individual. A user could then re-enable AI responses.
5. Flag users as spammers manually or automatically
6. Detect when someone had directly insulted the user, and respond with explicit text art
7. Detected presence of general swear words and respond with an inside community joke
8. Save user conversations so that Cleverbot could have some kind of meaningful conversation per user
9. Respond to detected Teamspeak events e.g getting kicked from a channel
10. If AFK, allow people to send "urgent" message that sends a notification to my iphone
11. Utilise an API to convert steam community links in to player ids
12. Ability to auto set avaialbility when in specific teamspeak channels


### Credits
----

Everyting in this script was created by myself.

Credits to developers of the following requirements:
- pyTson (The plugin that my script was created for)
- Cleverbot
- Steam Package for converting community links to steam ID's
- Pushover API