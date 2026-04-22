#  RateMe Bot

A Telegram bot for creating profiles, meeting new people, and rating other users' profiles.

##  Key Features
* **Profile Creation:** Users can set up their profile with a photo, age, gender, bio, and dating preferences.
* **Rating System:** Ability to rate other profiles on a scale from 1 to 10.
* **Smart Feed:** An algorithm that filters out recently viewed profiles (12-hour timeout) to keep the feed fresh.
* **Push Notifications:** Instant alerts when a user receives a high rating (7+).
* **Dynamic Menu:** Interactive keyboard buttons that display the real-time count of new, unseen likes.

##  Tech Stack
* **Language:** Python 3
* **Library:** `pyTelegramBotAPI` (Telebot)
* **Database:** `JSON` (Local data storage)

##  How to Run Locally
1. Clone the repository:
   `git clone https://github.com/your_username/titinto-bot.git`
2. Create a `config.py` file in the root directory and add your bot token:
   `TOKEN = "your_botfather_token_here"`
3. Run the bot:
   `python TitintoMain.py`
