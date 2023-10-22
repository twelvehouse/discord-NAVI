# discord-NAVI
Discord chatbot for personal use.[^1]  

___lets all love lain___

## Features
- easily set up a chatbot-only channel using the channel topic
- because it uses conversation_id, the conversation will continue even if the BOT is restarted
- `reset` command can be used to restore the effect of custom instructions
- with heartbeat function to check if BOT is still running (in DM)
- access_token and conversation_id can be updated at any time from the command


## How to use
1. install requirements `pip install -R requirements.txt`
2. create `config.ini` based on `example_config.ini` in `config/`
3. create .env file if you need.
    > for example, if you want to set `CHATGPT_BASE_URL`  
    > The reverse proxy used by default in revChatGPT.V1 is no longer available.

4. change the topic of the channel you want to chat in to the one you set in `config.ini`
5. run `python bot.py`

[^1]: ikitte eigo de readme kakuno tanosi