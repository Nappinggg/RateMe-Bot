# registration.py
import telebot
from buttons import Keyboards


# mixin - class that add functions to main bot
class RegistrationSystem:
    #Type hints for attributes provided by the main class
    bot: telebot.TeleBot
    users: dict
    allowed_genders: list
    allowed_choices: list

    def back_to_menu(self, message):
        pass

#----REGISTRATION
    def start_reg(self, message):
        msg = self.bot.send_message(message.chat.id, "Як тебе звати? (Напиши ім'я)",
                                    reply_markup=Keyboards.cancel_markup())
        self.bot.register_next_step_handler(msg, self.process_name_step)

    # 1st STEP: Name
    def process_name_step(self, message):
        try:
            if message.text == "🚫 Скасувати":
                self.back_to_menu(message)  # Цей метод "прилетить" з головного файлу
                return

            name = message.text
            msg = self.bot.send_message(message.chat.id, "Ти хлопець чи дівчина?",
                                        reply_markup=Keyboards.gender_markup())
            self.bot.register_next_step_handler(msg, self.process_gender_step, name)
        except Exception as e:
            self.bot.reply_to(message, "Помилка. Натисни /start")
            print(f"Error Reg Name: {e}")

    # 2nd STEP: Gender
    def process_gender_step(self, message, name):
        try:
            gender = message.text
            if gender not in self.allowed_genders:
                msg = self.bot.reply_to(message, "⚠️ Натисни кнопку нижче! 👇", reply_markup=Keyboards.gender_markup())
                self.bot.register_next_step_handler(msg, self.process_gender_step, name)
                return

            msg = self.bot.send_message(message.chat.id, "Скільки тобі років?", reply_markup=Keyboards.hide())
            self.bot.register_next_step_handler(msg, self.process_age_step, name, gender)
        except Exception:
            self.bot.reply_to(message, "Помилка. Натисни /start")

    # 3rd STEP: Age
    def process_age_step(self, message, name, gender):
        try:
            age_text = message.text
            if not age_text.isdigit():
                msg = self.bot.reply_to(message, "⚠️ Введи вік цифрами!", reply_markup=Keyboards.hide())
                self.bot.register_next_step_handler(msg, self.process_age_step, name, gender)
                return

            age = int(age_text)

            if age < 14 or age > 99:
                msg = self.bot.reply_to(message, "⚠️ Будь ласка, введи реальний вік (від 14 до 99)!",
                                        reply_markup=Keyboards.hide())
                self.bot.register_next_step_handler(msg, self.process_age_step, name, gender)
                return

            # ask for descriptio
            msg = self.bot.send_message(message.chat.id, "Напиши короткий опис про себе (до 200 символів):")
            self.bot.register_next_step_handler(msg, self.process_desc_step, name, gender, age)
        except Exception:
            self.bot.reply_to(message, "Помилка. Натисни /start")

    # 4th STEP: Description
    def process_desc_step(self, message, name, gender, age):
        try:
            desc = message.text

            # limit of 200 symbols
            if len(desc) > 200:
                msg = self.bot.reply_to(message,
                                        f"⚠️ Твій опис задовгий ({len(desc)}/150 символів).\nНапиши трохи коротше:")
                self.bot.register_next_step_handler(msg, self.process_desc_step, name, gender, age)
                return

            # if everything ok --> take photo
            msg = self.bot.send_message(message.chat.id, "📸 Надішли своє фото (картинкою)")
            self.bot.register_next_step_handler(msg, self.process_photo_step, name, gender, age, desc)
        except Exception:
            self.bot.reply_to(message, "Помилка. Натисни /start")

    # 5th STEP: Photo
    def process_photo_step(self, message, name, gender, age, desc):  # <-- додали desc
        try:
            if not message.content_type == 'photo':
                msg = self.bot.reply_to(message, "⚠️ Це не фото!")
                self.bot.register_next_step_handler(msg, self.process_photo_step, name, gender, age, desc)
                return
            photo_id = message.photo[-1].file_id

            msg = self.bot.send_message(message.chat.id, "Кого ти хочеш оцінювати?",
                                            reply_markup=Keyboards.choice_markup())
            self.bot.register_next_step_handler(msg, self.process_choice_step, name, gender, age, desc, photo_id)

        except Exception as e:
            self.bot.reply_to(message, "Помилка. Натисни /start")
            print(f"Error: {e}")

    # 6th STEP: Choice
    def process_choice_step(self, message, name, gender, age, desc, photo_id):  # <-- додали desc
        try:
            choice = message.text
            if choice not in self.allowed_choices:
                msg = self.bot.reply_to(message, "⚠️ Натисни кнопку нижче! 👇",
                                        reply_markup=Keyboards.choice_markup())
                self.bot.register_next_step_handler(msg, self.process_choice_step, name, gender, age, desc,
                                                        photo_id)
                return

            user_id = str(message.chat.id)

            old_scores = []
            if user_id in self.users:
                old_scores = self.users[user_id].get('scores', [])

            self.users[user_id] = {
                'name': name,
                'gender': gender,
                'age': age,
                'description': desc,
                'photo': photo_id,
                'preference': choice,
                'scores': old_scores,
                'is_active': True
            }

            self.db.save(self.users)

            # show description
            caption_text = f"✨ **Анкета збережена!** ✨\n\n👤 Ім'я: {name}\n👫 Стать: {gender}\n🎂 Вік: {age}\n📝 Про себе: {desc}\n🔍 Кого шукаю: {choice}\n\nОбери дію в меню 👇"

            self.bot.send_photo(message.chat.id, photo_id, caption=caption_text, parse_mode="Markdown",
                                reply_markup=Keyboards.main_menu())
        except Exception as e:
            self.bot.reply_to(message, "Помилка. Натисни /start")
            print(f"Error saving: {e}")