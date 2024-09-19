# Anonymous Confession Bot

A Discord bot for managing anonymous confessions with features for submission, configuration, banning/unbanning users, and exposing confessions. 
Unfortunately we do not live in a perfect world and people will abuse a 100% anonymous confession bot but this one is written with privacy in mind!
It only logs the last 5 confessions(By default) anything after is swipped away to the void, and if a staff memeber chooses to expose you to find out who wrote what confession both the staff memeber and the user involved get a DM.

## Features

- **Submit Anonymous Confessions**: Users can submit anonymous confessions to specified channels.
- **Configure Settings**: Administrators can set up roles and channels for confession handling.
- **Ban/Unban Users**: Ban or unban users from using the confession bot based on confession history.
- **Expose Confessions**: Expose specific confessions and notify involved users.

## Requirements

- Python 3.8 or higher
- Required Python libraries listed in `requirements.txt`

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Nam0/ConfessionBot/
   cd ConfessionBot
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Required Packages**

   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare Configuration**

   - Create a folder named `server_configs` in the same directory as your script.
   - Add a configuration file for each server (e.g., `123456789012345678.json`) inside the `server_configs` folder.
   - Use the sample configuration file as a template:
     ```json
     {
       "admin_roles": [],
       "confession_channel_ids": [],
       "banned_users": [],
       "confessions": []
     }
     ```

## Bot Setup

1. **Create a Discord Bot**

   - Go to the [Discord Developer Portal](https://discord.com/developers/applications).
   - Create a new application and add a bot to it.
   - Under **OAuth2**, give the bot the following scopes:
     - `Bot`
     - `application.commands`
   - Under **Bot Permissions**, select:
     - Send Messages
     - Manage Messages
     - Read Message History
     - Use Slash Commands

2. **Enable Message Content Intent**

   - Under **Bot**, toggle the `Message Content Intent` permission.

3. **Invite the Bot to Your Server**

   - Generate an OAuth2 invite link and add the bot to your server.

## Running the Bot

1. Replace `'YourBotTokenHere'` in the script with your bot's token.

2. Run the bot:

   ```bash
   python bot_script.py
   ```

   (Replace `bot_script.py` with the name of your script file.)

## Usage

- **/confess**: Submit an anonymous confession.
- **/configure**: Configure server settings for the confession bot.
- **/confession_ban**: Ban a user from using the confession bot based on confession number.
- **/confession_unban**: Unban a user from using the confession bot.
- **/expose**: Expose a confession and notify involved users.

## Contributing

Feel free to open issues or submit pull requests if you have suggestions or improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
