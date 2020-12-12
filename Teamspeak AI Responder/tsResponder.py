"""
File: tsResponder.py
Purpose: Respond automatically to direct messages on teamspeak client
Author: Jack Devonshire
"""

#PyTSon Requirements
from PythonQt.QtCore import QTimer
from PythonQt.Qt import QApplication
from ts3plugin import ts3plugin, PluginHost
import ts3lib, ts3defines, ts3client
from PythonQt.QtSql import QSqlDatabase

#Main Requirements
import os
import cleverbot
cb = cleverbot.Cleverbot(os.environ["autoTeamspeakCleverbotKey"], timeout=60, tweak1=15, tweak2=95, tweak3=85)
import steam 
import re
import time
import requests


#IOS Notification Setup
from pushover import init, Client #https://github.com/Thibauth/python-pushover
#https://pushover.net/apps/agd24h79j724stywc93s2e35se5vsz
iphone = Client(os.environ["autoTeamspeakPushoverKey"], api_token=os.environ["autoTeamspeakPushoverToken"])

class tsResponder(ts3plugin):
    name = "Teamspeak AI Responder"
    requestAutoload = False
    version = "1.0.1"
    apiVersion = 21
    author = "Jack Devonshire"
    description = "Auto Responder"
    offersConfigure = False
    commandKeyword = ""
    infoTitle = None
    menuItems = [
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 99, "=== AI Responder ===", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Permenant: Status Available", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Permenant: Status Unavailable", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 2, "Remove Permenant Status", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 99, "====================", ""),

        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 99, "=== AI Responder ===", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 3, "Set AI Respond", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 4, "Set AI Ignore", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 5, "End Chat [Silent]", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 6, "End Chat [Notify User]", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 7, "Flag as Spammer", ""),
        (ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CLIENT, 8, "Remove Spammer Flag", ""),
        
        #(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 99, "=== AI Responder ===", ""),
        #(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 5, "When in channel: Available", ""),
        #(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 6, "When in channel: Unavailable", ""),
        #(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_CHANNEL, 99, "====================", ""),
    ]
    hotkeys = []

    def __init__(self):
        self.settings = ts3client.Config()
        self.available = True
        self.permAvailability = 0 #0 = Off, 1 = Perm Available, 2 = Perm Unavailable
        self.savedConvos = {}
        f = open(r'E:\Programs\Teamspeak\config\plugins\pyTSon\scripts\tsResponder\ignore.txt', 'r+')
        self.ignoreList = [line[:-1] for line in f]
        self.rudeWords = ["redacted", "for", "portfolio"]
        self.links = {'Handbook': '<redacted for portfolio>',
                      'Application': '<redacted for portfolio>',
                      'Apply': '<redacted for portfolio>',
                      'Roster': '<redacted for portfolio>',
                      'CSO Guide': '<redacted for portfolio>',
                      'Guide': '<redacted for portfolio>',
                      'Ticket': '<redacted for portfolio>',
                      'Fines': '<redacted for portfolio>',
                      'Returning': '<redacted for portfolio>',
                      'Feedback': '<redacted for portfolio>',
                      'Whisper': '<redacted for portfolio>',
                      'loa': '<redacted for portfolio>'
                      }
        self.times = {'PPCE': 'Two days after your Interview', 
                      'PPC': 'Once you are Whitelisted',
                      'FA': '2 days after your PPCE',
                      'Field Assessment': '2 days after your PPCE'}
        


    def updateIgnoreList(self):    
        f = open(r'E:\Programs\Teamspeak\config\plugins\pyTSon\scripts\tsResponder\ignore.txt', 'r+')
        f.truncate(0)
        f.close()
        
        with open(r'E:\Programs\Teamspeak\config\plugins\pyTSon\scripts\answercontacts\ignore.txt', 'w') as f:
            for item in self.ignoreList:
                f.write("%s\n" % item)
        return

        
    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        (err, uid) = ts3lib.getClientVariable(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
        if menuItemID == 0:
            self.permAvailability = 1
            ts3lib.printMessageToCurrentTab("Status Change: Now Permenantly Available")
        elif menuItemID == 1:
            self.permAvailability = 2
            ts3lib.printMessageToCurrentTab("Status Change: Now Permenantly Unvailable")
        elif menuItemID == 2:
            self.permAvailability = 0
            if self.available == True:
                ts3lib.printMessageToCurrentTab("Status Change: Now Available")
            else:
                ts3lib.printMessageToCurrentTab("Status Change: Now Unavailable")


        elif menuItemID == 3 or menuItemID == 4: #Set AI Respond or Set AI Ignore
            #Checking client and getting variables etc
            (err, ownID) = ts3lib.getClientID(schid)
            if selectedItemID == ownID: return
            (err, uid) = ts3lib.getClientVariable(schid, selectedItemID, ts3defines.ClientProperties.CLIENT_UNIQUE_IDENTIFIER)
            if not uid: return

                
            ##Updating ignore.txt
            f = open(r'E:\Programs\Teamspeak\config\plugins\pyTSon\scripts\tsResonder\ignore.txt', 'r+')
            self.ignoreList = [line[:-1] for line in f]

            
            if menuItemID == 3 and uid in self.ignoreList: #Set AI Respond
                self.ignoreList.remove(uid)
                
            if menuItemID == 4 and (uid not in self.ignoreList): #Set AI Ignore
                self.ignoreList.append(uid)
            
            self.updateIgnoreList()

            ts3lib.printMessageToCurrentTab("Status Updated For: " + str(uid))

        elif menuItemID == 5 or menuItemID == 6:
            if selectedItemID in self.savedConvos:
                self.savedConvos[selectedItemID][3] = False #The AI Will now respond to them again
            else:
                self.savedConvos[selectedItemID] = [cb.conversation(), 0, (int(round(time.time()) * 1000)), False]
            if menuItemID == 6:
                err = ts3lib.requestSendPrivateTextMsg(schid, "[AI] I have ended this chat. AI Responses activated.", selectedItemID)
            return
        
        elif menuItemID == 7 or menuItemID == 8: #Spam Mode Check
            if selectedItemID in self.savedConvos:
                if menItemID == 7:
                    self.savedConvos[selectedItemID][4] = True
                else:
                    self.savedConvos[selectedItemID][4] = False
            else:
                if menuItemID == 7:
                    self.savedConvos[selectedItemID] = [cb.conversation(), 0, (int(round(time.time()) * 1000)), False, True]
                else:
                    self.savedConvos[selectedItemID] = [cb.conversation(), 0, (int(round(time.time()) * 1000)), False, False]
                    
        elif menuItemID == 20:
            self.joinOnSupport = True

        elif menuItemID == 21:
            self.joinOnSupport = False


    def onClientKickFromChannelEvent(self, schid, clientID, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage):
        (err, myid) = ts3lib.getClientID(schid)
        if clientID != myid or kickerID == myid: return
        message = "[AI] Listen here " + kickerName + " I don't apreciate you kicking me from the channel! :("
        err = ts3lib.requestSendPrivateTextMsg(schid, message, kickerID)



    def onTalkStatusChangeEvent(self, schid, status, isReceivedWhisper, clid):
        if isReceivedWhisper == 0:
            return

        err, name = ts3lib.getClientVariableAsString(schid, clid,ts3defines.ClientProperties.CLIENT_NICKNAME)
        content = "Whisper | " + name
        iphone.send_message(content, title=content)

        
    def onTextMessageEvent(self, schid, targetMode, toID, fromID, fromName, fromUniqueIdentifier, message, ffIgnored):
        (err, myid) = ts3lib.getClientID(schid)
        (err, curChannelID) = ts3lib.getChannelOfClient(schid, toID)
        message = message.lower()


        if err == ts3defines.ERROR_ok:
            if '[AI]'.lower() in message:
                return
            if fromUniqueIdentifier == '<redacted for portfolio>': #If message sent by bot or own identifier
                if '[AI]'.lower() in message:
                    return
                else:
                    if not ('endchat' in message):
                        if toID in self.savedConvos:
                            if not self.savedConvos[toID][3]:
                                ts3lib.printMessageToCurrentTab("Chat Started | AI Will not respond to this client until you type 'endchat' or select it in the menu!")
                            self.savedConvos[toID][3] = True #The bot will not message them whilst I am talking to them. True = I am ina  conversation with them
                        else:
                            ts3lib.printMessageToCurrentTab("Chat Started | AI Will not respond to this client until you type 'endchat' or select it in the menu!")
                            self.savedConvos[toID] = [cb.conversation(), 0, (int(round(time.time()) * 1000)), True, False]
                if 'endchat' in message:
                    if fromUniqueIdentifier in self.ignoreList:
                        return
                    self.savedConvos[toID][3] = False # The AI Will now respond to them again
                    err = ts3lib.requestSendPrivateTextMsg(schid, "[AI] I have ended this chat. AI Responses activated.", toID)
                    return
                return
                    
            
            if toID == myid:
                if fromUniqueIdentifier == "redacted for portfolio": #Do not respond to Community Teamspeak Bot
                    return
                    
                message = message.lower()

                ##### Bot On/Off Commands #####
                if 'stopai' in message or 'stop ai' in message:
                    self.ignoreList.append(fromUniqueIdentifier)
                    self.updateIgnoreList()
                    err = ts3lib.requestSendPrivateTextMsg(schid, "[AI] AI Stopped. Type 'startai' to allow AI Responses.", fromID)
                    return
                
                if 'startai' in message or 'start ai' in message:
                    self.ignoreList.remove(fromUniqueIdentifier)
                    self.updateIgnoreList()
                    err = ts3lib.requestSendPrivateTextMsg(schid, "[AI] AI Started. Type 'bothelp' for help.", fromID)
                    return
                
                if fromUniqueIdentifier in self.ignoreList: #Do not respond to clients on ignore list
                    return

                for word in self.rudeWords:
                    if word in message:
                        if "you" in message:
                            response = """[AI] Don't swear at me! <explicit text art redacted for portfolio>"""
                            err = ts3lib.requestSendPrivateTextMsg(schid, response, fromID)
                            return
                        else:
                            err = ts3lib.requestSendPrivateTextMsg(schid, "[AI] NAUGHTY WORD DETECTED. Stop being rude!", fromID)
                        return

                    
                

                #self.available = True/False
                #0 = Perm Not on
                #1 = Perm Available
                #2 = Perm Unavailable

                if ((not self.available) and (self.permAvailability != 1)) or (self.permAvailability == 2):

                    ##### Core Bot Commands #####
                    if fromID in self.savedConvos:
                        details = self.savedConvos[fromID]
                        self.savedConvos[fromID][2] = int(round(time.time() * 1000))
                        if self.savedConvos[fromID][3]: #If I have messaged them the AI will not respond until I end the conversation with the command 'endchat'
                            return

                    else:
                        self.savedConvos[fromID] = [cb.conversation(), 0, (int(round(time.time()) * 1000)), False, False] # [Object, amount of urgent requests sent, time sent (in secs), Currently talking to them [True/False], spam mode activated/deactivated]
                        details = self.savedConvos[fromID]
                        response = "[AI] Hey! I am unavailable right now. Please speak to my AI. [Type 'bothelp' for more commands]"
                        err = ts3lib.requestSendPrivateTextMsg(schid, response, fromID)


                    
                    if 'bothelp' in message or 'bot help' in message:
                        response = """[AI]
[b][AI Command List][/b]
- Send any message to talk to the AI
- 'bothelp' - Recieve this list
- 'stopai' - Permenantly stop AI responses
- 'startai' - Permenantly allow AI responses
[b][Police Information][/b]
This bot can give you the following Police Information:
- Most Police Links - e.g 'Can I have the handbook link please?'
- Times between Academy training/tests - e.g 'How long until I can do my PPCE?'
[b][My Information][/b]
- 'alexpid' - Get my PlayerID
- 'alexforum' - Get my Forum Link
- 'URGENT' - Will notify my phone. Can be used twice per TS session.
[b][Tools][/b]
- 'steamid <steam profile link> - Get your Steam64 ID
- 'setpid <steamid>' - Save your Steam ID to my Database
- 'setforumid <steamid>' - Save your Forum ID to my Database
                        """
                        
                        err = ts3lib.requestSendPrivateTextMsg(schid, response, fromID)
                        return

                    
                    ##### Police Responses #####
                    sent = False
                    if 'alexpid' in message:
                        err = ts3lib.requestSendPrivateTextMsg(schid, 'My PlayerID is <redacted for portfolio>', fromID)
                        return
                    if 'alexforum' in message:
                        err = ts3lib.requestSendPrivateTextMsg(schid, 'Here is my [url=<redacted for portfolio>]Forum Link[/url]', fromID)
                        return
                    if 'urgent' in message:
                        if self.savedConvos[fromID][1] < 2:
                            self.savedConvos[fromID][1] += 1
                            iphone.send_message(("Urgent Request from: " + str(fromUniqueIdentifier)), title="Urgent")
                            err = ts3lib.requestSendPrivateTextMsg(schid, '[AI] Phone Notified. I will get back to you ASAP.', fromID)
                        else:
                            err = ts3lib.requestSendPrivateTextMsg(schid, '[AI] Error. You have run out of urgent requests.', fromID)
                        return
                        
                    #Main Police Link Responses
                    for key in self.links:
                        if key.lower() in message:
                            sent = True
                            response = "[AI] Did you want this link? > " + "[url=" + self.links[key] + "]" + key + "[/url]"
                            err = ts3lib.requestSendPrivateTextMsg(schid, response, fromID)

                    #Academy Wait Times Responses
                    if 'time' in message or 'long' in message or 'when' in message:
                        for key in self.times:
                            if key.lower() in message:
                                sent = True
                                response = "[AI] You can do your " + key + " " + self.times[key]
                                err = ts3lib.requestSendPrivateTextMsg(schid, response, fromID)

                    ##### PlayerID Tools #####
                    if 'playerid' in message or 'steamid' in message or 'steam id' in message or 'player id' in message:
                        sent = True
                        regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
                        match = re.findall(regex, message)
                        if not match:
                            err = ts3lib.requestSendPrivateTextMsg(schid, "[AI] Whoops. You need to use this command in conjunction with your Steam Community Link.", fromID)
                            return
                        pid = steam.steamid.steam64_from_url(match[0])

                        if 'steamcommunity.com/profiles' in match[0]:
                            match[0] = match[0].replace('www', '')
                            match[0] = match[0].replace('0', '')
                            match[0] = match[0].replace('http:', '')
                            match[0] = match[0].replace('https:', '')
                            match[0] = match[0].replace('/', '')
                            match[0] = match[0].replace('steamcommunity.comprofiles', '')
                            match[0] = match[0].replace('[url]', '')
                            try:
                                match[0] = int(match[0])
                                pid = match[0]
                            except:
                                pid = None

                            if not pid:
                                err = ts3lib.requestSendPrivateTextMsg(schid, match[0], fromID)
                                err = ts3lib.requestSendPrivateTextMsg(schid, "[AI] Whoops. You need to use this command in conjunction with your Steam Community Link.", fromID)
                                return
                        err = ts3lib.requestSendPrivateTextMsg(schid, ("[AI] Your PlayerID is: " + str(pid)), fromID)

                    ##### After Training Links #####
                    if 'passinterview' in message:
                        response = """[AI]
[b][Congratulations, you have passed your interview!][/b]
[url=<redacted for portfolio>]Academy Feedback Form[/url]
[url=<redacted for portfolio>]CSO Guide[/url]
[url=<redacted for portfolio>]Police Handbook[/url]
[url=<redacted for portfolio>]Whisper Setup[/url]
Join the following [url=<link redacted for portfolio>]Discord[/url]
In #tagrequests, Type 'APC, Trainee'
In #whitelist-request, Type 'CSO'
You can do your PPC after you are whitelisted ingame.
                        """
                        err = ts3lib.requestSendPrivateTextMsg(schid, response, fromID)
                        sent = True

                    if sent: return

                    response = "[AI] " + details[0].say(message)
                    err = ts3lib.requestSendPrivateTextMsg(schid, response, fromID)
