## Introduction
For GIT (Github) testing only! Finance bot is simple python bot for for accounting expenses and income.
## Current Releases
0.1 - Initial commit. <br />
## Platforms
Any Linux. Python3 and python-pip3 required. Just launch it on any Linux system, no matter what internet connection(NAT or direct internet) you have.<br />
Required python libraries installation: <br />
```bash
pip install python-telegram-bot
pip install prettytable
pip install db-sqlite3
```
## Config file
Configure setting in config.py: <br />
* TELE_KEY is your telegram bot api key; <br />
* USERS is your your allowed users ID's (you can have many users as you want, separate them with commas);<br />
* DB_PATH is path for SQLite database for records;
## Usage
Typical launch: *python finance_bot.py* or *python3 finance_bot.py*. You can run it in a background mode (*python finance_bot.py &*) or run in a screen (or tmux) window.
## Bot commands
 * /start - Starts the bot and shows if you can use the bot. You can also find your user id using this command;
 * отчет [date] [category] - Shows top-ups and costs for the current date (if there is no date), or for a specific day (if the date is in the format '20.10.2022'), or for the current month (if the date is in the format '10.2022');
 * \+ amount [date] [category] - Adds a budget deposit entry. If a date in the format '10.20.2022' is omitted, then the deposit will be by current date. If the category is missing, then the category will be 'Прочие';
 * \- amount [date] [category] Adds a write-off entry from the budget. If a date in the format '10.20.2022' is omitted, then the entry will be will be by current date. If the category is omitted, then the category will be 'Прочие';<br />
 Note: the category is case-sensetive, because SQLite can't to convert to lowercase cyrillic letters.
## How can I get telegram API key?
Install telegram and find BotFather in search window. Now type: <br />
*/newbot* <br />
Now enter the name and bot father will generate a key for you.<br />
Additionally you can set avatar for your bot: <br />
*/setuserpic* <br />
BotFather will ask you for bot name. Enter you  bot's name from first step and press enter, then send any picture you like as photo (not like file).
## Licenses
Use and modify on your own risk.
