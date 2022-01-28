# DaryNode Support Bot

This bot was designed by the DaryNodes dev team for support on the official DaryNodes discord server.

## Installation instructions

1. clone the repository:
   ```sh
   git clone https://github.com/DaryNode/DaryNode-Support.git
   ```
2. Install the requirments:
   ```sh
   pip install -r requirements.txt
   ```
3. configuration (Find config instructions below!):
   ```sh
   cp config.example.json config.json
   ```
4. Run the bot:
   ```sh
   python3 bot.py
   ```

## Configuration

Bot congiguration is done in the config.json file.

`token`: The bot token from discord, learn how to get it [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token)

`prefix`: The prefix for the bot, this is the command that the bot will listen to.

`mongoDB_connection_url`: The url to the mongoDB database.

`mongoDB_database_name`: The name of the database on mongodb(database needs to have a few things preconfigured, I will add that info soon).

## Contributing:

Will add this soon
