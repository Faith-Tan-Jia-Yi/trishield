# **Guide on Trishield**

## 1. How to set up the bot
### After cloning the repositiory, create a .env file. In the .env file, add the following line.

```
DISCORD_TOKEN=<your-token-here>
```

### Your 'DISCORD_TOKEN' can be found after creating an application here https://discord.com/developers/applications. 
### For a detailed guide on how to create a new application on discord and retrieve the 'DISCORD_TOKEN', please refer to https://realpython.com/how-to-make-a-discord-bot-python/#creating-an-application.

### You may also need to install nltk, google api client among other things if they are not yet installed. 

## 2. How to use the bot

### Run the bot by running the file 'main.py'. If you get the message *TrishieldBot#XXX is now running!* it means that the bot is successfully online and can be used.

## 3. What are the features
- Bot runs in the background, normal (non-toxic) messages are not affected.
- When the message includes something that is deemed toxic to the community, the bot will prompt the user to use the /t command to send the message. 
- Moderators are able to edit the banned word list (csv file) and change what words are banned and flagged.

## 4. Conversation Flow Examples
    
(1) Non-Toxic Messages

```mermaid
graph TD;
    A[user sends message]-->B[trishieldn deems non-toxic];
    B[trishield deems non-toxic]-->C[message is sent];

```

(2) Toxic Messages
```mermaid
graph TD;
    A[user sends message]-->B[trishield deems toxic];
    B[trishield deems toxic]-->C[trishield removes the toxic message];
    C[trishield removes the toxic message]-->D[trishield sends a temporary prompt message telling the user to use /t];
    D[trishield sends a temporary prompt message telling the user to use /t]-->E[user uses the command /t];
    E[user uses the command /t]-->F[a trishield intervention module is pulled up];
    F[a trishield intervention module is pulled up]-->G[the user's previous toxic message is shown again];
    G[the user's previous toxic message is shown again]-->H[user is notified that the message is deemed toxic and is given a chance to rewrite the message];
    H[user is notified that the message is deemed toxic and is given a chance to rewrite the message]-->I[user edits the message];
    H[user is notified that the message is deemed toxic and is given a chance to rewrite the message]-->J[user does not edit the message];
    I[user edits the message]-->L[trishield deems toxic]
    I[user edits the message]-->M[trishield deems non-toxic]
    M[trishield deems non-toxic]-->N[trishield sends out the message on behalf of the user with the user's profile tagged to it]
    J[user does not edit the message]-->K[user recieves a module warning that the message is flagged as toxic and prompted to either edit the message or send it anyways]
    L[trishield deems toxic]-->K[user recieves a module warning that the message is flagged as toxic and prompted to either edit the message or send it anyways]
   K[user recieves a module warning that the message is flagged as toxic and prompted to either edit the message or send it anyways]-->O[user choose to edit]
   O[user choose to edit]-->H[user is notified that the message is deemed toxic and is given a chance to rewrite the message]
   K[user recieves a module warning that the message is flagged as toxic and prompted to either edit the message or send it anyways]-->Q[user choose to send anyways]
   Q[user choose to send anyways]-->R[trishield sends out the message on behalf of the user with the user's profile tagged to it. trishield censors the message with the spoiler tag and warns other users that there might be a trigger warning.]

```
