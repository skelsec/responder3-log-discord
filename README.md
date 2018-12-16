# responder3-log-discord
Discord logging extension for Responder3

# Prerequisites
**discord.py is currently broken with python 3.7, install from git.**
install [Responder3](https://github.com/skelsec/Responder3) first

# Install
```
pip install https://github.com/skelsec/responder3-log-discord/archive/master.zip#egg=responder3-log-discord
```

now update mismatched depends
- `pip install -U https://github.com/Rapptz/discord.py/archive/async.zip#egg=discord.py`
- `pip install -U aiohttp`
- `pip install -U websockets`


# Config

```
logsettings = {
        'handlers':{
                'discord': ['discord'],
        },
        'discord' : {
                'token' : '<your bot token>',
                'channel' : '<target channel id>',
                'extra_info':'localhost',
                'log_connections': True, #only enable this is you want to drown in messages!
        },
<snip>
}
```

## Channel ID
Enable [discord developer](https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-) mode and right click the target channel to get the channel id
