from telebot import types


class Keyboards:
    @staticmethod
    def start_markup():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Створити анкету"))
        return markup

    @staticmethod
    def cancel_markup():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("🚫 Скасувати"))
        return markup

    @staticmethod
    def gender_markup():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn1 = types.KeyboardButton("Хлопець")
        btn2 = types.KeyboardButton("Дівчина")
        markup.row(btn1, btn2)
        return markup

    @staticmethod
    def choice_markup():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn1 = types.KeyboardButton("Хлопці")
        btn2 = types.KeyboardButton("Дівчата")
        btn3 = types.KeyboardButton("Не важливо")
        markup.row(btn1, btn2)
        markup.row(btn3)
        return markup

    @staticmethod
    def confirm_delete_markup():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn_yes = types.KeyboardButton("✅Так, видалити")
        btn_no = types.KeyboardButton("❌Ні, я передумав")
        markup.row(btn_yes, btn_no)
        return markup

    @staticmethod
    def main_menu(new_likes_count=0):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🚀 Оцінювати анкети")
        btn2 = types.KeyboardButton("👤 Моя анкета")
        btn3 = types.KeyboardButton("✏️ Змінити анкету")
        #dynamic button. works as notification
        if new_likes_count > 0:
            btn4 = types.KeyboardButton(f"💌 Хто мене оцінив ({new_likes_count})")
        else:
            btn4 = types.KeyboardButton("💌 Хто мене оцінив")
        btn5 = types.KeyboardButton("🗑️ Видалити анкету")
        btn6 = types.KeyboardButton("💤 Відключити/включити мою анкету")
        markup.row(btn1, btn2)
        markup.row(btn3, btn4)
        markup.row(btn5, btn6)
        return markup

    @staticmethod
    def rating_markup():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # rating buttons
        btns_1_to_5 = [types.KeyboardButton(str(i)) for i in range(1, 6)]
        btns_6_to_10 = [types.KeyboardButton(str(i)) for i in range(6, 11)]
        markup.row(*btns_1_to_5)
        markup.row(*btns_6_to_10)
        # exit button
        btn_exit = types.KeyboardButton("🏁 Досить")
        markup.row(btn_exit)

        return markup

    @staticmethod
    def hide():
        return types.ReplyKeyboardRemove()