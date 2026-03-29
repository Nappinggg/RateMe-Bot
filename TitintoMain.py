############################################################################################
####   New bot from old idea based on BIBINTO.                                           ###
####   This bot helps you get a quick photo rating and short feedback from other users.  ###
####    How it works:                                                                    ###
####       Create profile.                                                               ###
####       Wait while other users rate it and leave comments.                            ###
####       Check your average score and read the feedback.                               ###
####   By @nappinggg                                                                     ###
############################################################################################

# Imports
import telebot
import random
from database import JSONDatabase
from buttons import Keyboards
from registration import RegistrationSystem
import config

# Configuration
TOKEN = config.TOKEN
DB_FILE = "users.json"


# ==========================================
# --- ДЕКОРАТОР ДЛЯ ПЕРЕВІРКИ АНКЕТИ ---
# ==========================================
def require_profile(func):
    """this decorator checks whether user has provile"""

    def wrapper(self, message, *args, **kwargs):
        user_id = str(message.chat.id)
        if user_id not in self.users:
            self.bot.reply_to(message, "Спершу створи свою анкету!", reply_markup=Keyboards.start_markup())
            return  # stop
        return func(self, message, *args, **kwargs)

    return wrapper


class TitintoBot(RegistrationSystem):
    def __init__(self, token, db_filename):
        # Initialize bot and database
        self.bot = telebot.TeleBot(token)
        self.db = JSONDatabase(db_filename)
        self.users = self.db.load()  # Load users from database

        # Constants for profile
        self.allowed_genders = ["Хлопець", "Дівчина"]
        self.allowed_choices = ["Хлопці", "Дівчата", "Не важливо"]

        # Register handlers
        self.register_handlers()

    def register_handlers(self):
        # Command start
        self.bot.message_handler(commands=['start'])(self.handle_start)

        # Menu buttons logic
        self.bot.message_handler(func=lambda m: m.text == "👤 Моя анкета")(self.show_my_profile)
        self.bot.message_handler(func=lambda m: m.text == "🗑️ Видалити анкету")(self.delete_profile)
        self.bot.message_handler(func=lambda m: m.text == "🚀 Оцінювати анкети")(self.start_rating)
        self.bot.message_handler(func=lambda m: m.text == "💤 Відключити/включити мою анкету")(self.toggle_visibility)
        # use .startswith(), so bot reacting to "Хто мене оцінив", and to "Хто мене оцінив (5)"
        self.bot.message_handler(func=lambda m: m.text and m.text.startswith("💌 Хто мене оцінив"))(self.show_who_rated_me)

        # Create / edit profile trigger
        self.bot.message_handler(func=lambda m: m.text in ["Створити анкету", "/crProfile", "✏️ Змінити анкету"])(
            self.start_reg)

    def run(self):
        print("Bot is running...")
        self.bot.infinity_polling()

    # --- HELPER METHODS ---
    # average score calculation
    def get_formatted_rating(self, scores):
        if not scores:
            return "Ще немає оцінок"

        total_score = 0
        for s in scores:
            if isinstance(s, dict):  # new format
                total_score += s.get("score", 0)
            else:  # old format
                total_score += s

        avg_score = total_score / len(scores)
        return f"{round(avg_score, 1)}/10 ({len(scores)} оцінок)"

    # Cancel button HELPER
    def back_to_menu(self, message):
        user_id = str(message.chat.id)
        if user_id in self.users:
            likes_count = self.get_new_likes_count(user_id)
            markup = Keyboards.main_menu(likes_count)
            self.bot.send_message(message.chat.id, "❌ Дію скасовано. Ти в головному меню.", reply_markup=markup)
        else:
            markup = Keyboards.start_markup()
            self.bot.send_message(message.chat.id, "❌ Дію скасовано.", reply_markup=markup)

    #for button notifications. Shows how many people rated you
    def get_new_likes_count(self, user_id):
        if user_id not in self.users:
            return 0

        scores = self.users[user_id].get('scores', [])
        count = 0
        for s in scores:
            # search for new ratings > 7
            if isinstance(s, dict) and s.get("score", 0) >= 7 and not s.get("seen", False):
                # checks if user in database
                if s.get("rater_id") in self.users:
                    count += 1
        return count

    # --- HANDLERS ---

    # === 1. /start Command
    def handle_start(self, message):
        user_id = str(message.chat.id)

        # Revision. If user in the database already
        if user_id in self.users:
            # if yes - show general menu
            user_name = self.users[user_id]['name']
            likes_count = self.get_new_likes_count(user_id)
            markup = Keyboards.main_menu(likes_count)
            self.bot.reply_to(message, f"Привіт, {user_name}! Радий тебе бачити знову. 👋\nОбери дію в меню.",
                              reply_markup=markup)
        else:
            # if not - create profile
            markup = Keyboards.start_markup()
            self.bot.reply_to(message, "Привіт! Натисни кнопку 'Створити анкету', щоб почати.", reply_markup=markup)

    # === 2. Logic "My Profile" (👤 Моя анкета)
    @require_profile  # decorator
    def show_my_profile(self, message):
        # Завдяки декоратору ми 100% знаємо, що юзер існує, тому видалили перевірку "if user_id in self.users:"
        user_id = str(message.chat.id)
        user = self.users[user_id]

        # receiving data
        preference = user.get('preference', 'Не важливо')
        scores = user.get('scores', [])
        desc = user.get('description', 'Не вказано')
        # call function
        rating_text = self.get_formatted_rating(scores)
        caption_text = f"👤 Ім'я: {user['name']}\n👫 Стать: {user['gender']}\n🎂 Вік: {user['age']}\n📝 Про себе: {desc}\n🔍 Кого оцінюєм: {preference}\n⭐ Рейтинг: {rating_text}"
        self.bot.send_photo(message.chat.id, user['photo'], caption=caption_text)

    # === 3. Logic "Delete Profile" - confirmation (🗑️ Видалити анкету)
    @require_profile  # decorator
    def delete_profile(self, message):
        # Завдяки декоратору код став коротшим
        msg = self.bot.reply_to(
            message,
            "⚠️ **Ти впевнений, що хочеш видалити анкету?**\nВсі твої дані та оцінки будуть втрачені назавжди!",
            parse_mode="Markdown",
            reply_markup=Keyboards.confirm_delete_markup()
        )
        # pass next step
        self.bot.register_next_step_handler(msg, self.process_delete_confirmation)

    # actual logic "delete"
    def process_delete_confirmation(self, message):
        user_id = str(message.chat.id)
        # if yes
        if message.text == "✅Так, видалити":
            # remove from dictionary if yes
            if user_id in self.users:
                del self.users[user_id]
                self.db.save(self.users)

                markup = Keyboards.start_markup()
                self.bot.reply_to(message, "🗑️ Анкету успішно видалено. Сподіваюсь, ти ще повернешся!",
                                  reply_markup=markup)
            else:
                self.bot.reply_to(message, "Анкети вже немає.", reply_markup=Keyboards.start_markup())

        # if no
        elif message.text == "❌Ні, я передумав":
            # return to the menu
            likes_count = self.get_new_likes_count(user_id)
            markup = Keyboards.main_menu(likes_count)
            self.bot.reply_to(message, "Хух! Анкета на місці, все добре 😎", reply_markup=markup)

        # if entered smth different
        else:
            msg = self.bot.reply_to(message, "Натисни кнопку, щоб підтвердити або скасувати 👇",
                                    reply_markup=Keyboards.confirm_delete_markup())
            self.bot.register_next_step_handler(msg, self.process_delete_confirmation)

    # === 4. Logic "Hide profile" (Відключити мою анкету)
    @require_profile  # decorator
    def toggle_visibility(self, message):
        user_id = str(message.chat.id)
        # get current status
        current_status = self.users[user_id].get('is_active', True)

        # new status
        new_status = not current_status
        self.users[user_id]['is_active'] = new_status
        self.db.save(self.users)

        # reply to user
        if new_status == True:
            status_text = "🟢 **Ти знову в пошуку!** Твою анкету видно іншим."
        else:
            status_text = "💤 **Ти в режимі невидимки.** Твоя анкета прихована від інших."

        self.bot.reply_to(message, status_text, parse_mode="Markdown")

    # === 5. Logic "Rate people" (оцінити анкету)
    @require_profile  # decorator
    def start_rating(self, message):
        import time
        import random

        user_id = str(message.chat.id)
        current_user = self.users[user_id]

        # calculate likes for menu
        likes_count = self.get_new_likes_count(user_id)

        # check status (if not active user cannot rate others)
        if not current_user.get('is_active', True):
            self.bot.reply_to(message,
                              "💤 **Твоя анкета прихована.**\nЩоб оцінювати інших, ти маєш бути видимим. Включи свою анкету, щоб увімкнутись.",
                              parse_mode="Markdown", reply_markup=Keyboards.main_menu(likes_count))
            return

        try:  # age
            my_age = int(current_user['age'])
        except:
            my_age = 18  # just incase

        my_preference = current_user.get('preference', 'Не важливо')

        # diapason of people
        min_age = my_age - 1
        max_age = my_age + 1

        # smart queue
        candidates_new = []
        candidates_old = []

        now = time.time()
        TIMEOUT = 43200  # 12 hours in seconds (12 * 60 * 60)

        # history
        last_seen_dict = current_user.get('last_seen', {})

        for uid, profile in self.users.items():
            # dont show user's profile
            if uid == user_id:
                continue
            # ===1st FILTER=== Active or not
            if not profile.get('is_active', True):
                continue

            # ===2nd FILTER=== BY AGE
            try:
                candidate_age = int(profile['age'])
                if not (min_age <= candidate_age <= max_age):
                    continue
            except:
                continue

            # ===3rd FILTER=== BY PREFERENCE(GENDER)
            candidate_gender = profile.get('gender', '')
            if my_preference == "Хлопці" and candidate_gender != "Хлопець":
                continue
            if my_preference == "Дівчата" and candidate_gender != "Дівчина":
                continue

            # ===4th FILTER=== BY TIME (Розумна черга)
            if uid not in last_seen_dict:
                candidates_new.append(uid)  # Ще жодного разу не бачив
            elif now - last_seen_dict[uid] > TIMEOUT:
                candidates_old.append(uid)  # Бачив більше 12 годин тому

        # result (first -> new, second -> old)
        target_id = None
        if candidates_new:
            target_id = random.choice(candidates_new)
        elif candidates_old:
            target_id = random.choice(candidates_old)

        # if each of them empty - > no profile
        if not target_id:
            self.bot.reply_to(message,
                              f"😔 Анкети ({min_age}-{max_age} років) закінчилися або ти вже всіх оцінив.\nНові люди з'являться зовсім скоро, зазирни пізніше!",
                              reply_markup=Keyboards.main_menu(likes_count))
            return

        target_user = self.users[target_id]

        target_desc = target_user.get('description', '')
        desc_text = f"\n📝 Про себе: {target_desc}" if target_desc else ""

        # text with description
        caption = f"Оціни анкету:\n\n👤 {target_user['name']}, {target_user['age']} років ({target_user['gender']}){desc_text}"

        msg = self.bot.send_photo(message.chat.id, target_user['photo'], caption=caption,
                                  reply_markup=Keyboards.rating_markup())
        self.bot.register_next_step_handler(msg, self.process_rating_score, target_id)

    def process_rating_score(self, message, target_id):
        import time

        try:
            # exit
            if message.text == "🏁 Досить":
                self.back_to_menu(message)
                return

            # validation
            score = message.text
            if not score.isdigit() or int(score) < 1 or int(score) > 10:
                msg = self.bot.reply_to(message, "⚠️ Постав оцінку від 1 до 10!",
                                        reply_markup=Keyboards.rating_markup())
                self.bot.register_next_step_handler(msg, self.process_rating_score, target_id)
                return

            score_int = int(score)
            rater_id = str(message.chat.id)

            rating_data = {
                "rater_id": rater_id,
                "score": score_int,
                "seen": False  # Нова оцінка за замовчуванням не переглянута
            }

            # save rating
            self.users[target_id].setdefault('scores', []).append(rating_data)

            # === time seen ===
            if 'last_seen' not in self.users[rater_id]:
                self.users[rater_id]['last_seen'] = {}

            # in seconds for user
            self.users[rater_id]['last_seen'][target_id] = time.time()
            # =======================================

            self.db.save(self.users)

            # === notifications for my ratings* ===
            if score_int >= 7:
                try:
                    # calculate rating
                    target_likes = self.get_new_likes_count(target_id)
                    # special menu
                    target_markup = Keyboards.main_menu(target_likes)

                    self.bot.send_message(
                        target_id,
                        f"🔥 **Тебе оцінили на {score_int}/10!**\nЗазирни в меню 👇",
                        reply_markup=target_markup,
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    # if user blocked bot just ignore error
                    print(f"Could not notify user {target_id}: {e}")
            # ===============================================

            self.bot.send_message(message.chat.id, "✅ Оцінка зарахована!")

            # next
            self.start_rating(message)

        except Exception as e:
            print(f"Error rating: {e}")
            user_id = str(message.chat.id)
            likes_count = self.get_new_likes_count(user_id)
            self.bot.reply_to(message, "Сталася помилка.", reply_markup=Keyboards.main_menu(likes_count))

    # === 6. Logic "Who rated me" ( Хто мене оцінив)
    @require_profile
    def show_who_rated_me(self, message):
        user_id = str(message.chat.id)
        user = self.users[user_id]
        scores = user.get('scores', [])

        unseen_rater = None

        # the newest one
        # reversed() from new to old
        for s in reversed(scores):
            # check is its new rating system and >8
            if isinstance(s, dict) and s.get("score", 0) >= 7 and not s.get("seen", False):

                rater_id = s.get("rater_id")
                # check if that person hasnt deleted profile
                if rater_id in self.users:
                    unseen_rater = s
                    break  # stop when found
                else:
                    # if person deleted progile
                    s["seen"] = True

        # if all seen
        if not unseen_rater:
            self.db.save(self.users)  # just saving in case
            likes_count = self.get_new_likes_count(user_id)
            self.bot.reply_to(message, "💌 Поки що немає нових високих оцінок (7+). Зазирни сюди пізніше!",
                                reply_markup=Keyboards.main_menu(likes_count))
            return

        # 1. mark as seen and save it
        unseen_rater["seen"] = True
        self.db.save(self.users)

        likes_left = self.get_new_likes_count(user_id)
        markup = Keyboards.main_menu(likes_left)

        # 2. take person's details
        rater_id = unseen_rater["rater_id"]
        score = unseen_rater["score"]
        rater_profile = self.users[rater_id]

        r_name = rater_profile.get("name", "Невідомо")
        r_age = rater_profile.get("age", "?")
        r_gender = rater_profile.get("gender", "?")
        r_photo = rater_profile.get("photo")
        r_desc = rater_profile.get("description", "")

        # 3. create nice profile
        desc_text = f"\n📝 Про себе: {r_desc}" if r_desc else ""
        tg_link = f"[{r_name}](tg://user?id={rater_id})"

        caption = (
            f"💌 **Тебе оцінили на {score}/10!**\n\n"
            f"👤 {tg_link}, {r_age} років ({r_gender}){desc_text}\n\n"
            f"👇 *Тисни '💌 Хто мене оцінив' ще раз, щоб побачити наступного!*"
        )

        # 4. photo with description
        self.bot.send_photo(message.chat.id, r_photo, caption=caption,
                            parse_mode="Markdown", reply_markup=markup)

# Run the bot
if __name__ == "__main__":
    my_bot = TitintoBot(TOKEN, DB_FILE)
    my_bot.run()