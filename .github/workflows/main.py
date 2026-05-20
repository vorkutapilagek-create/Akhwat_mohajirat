import os
import telebot

# جلب توكن البوت بشكل آمن من بيئة تشغيل جيت هاب
TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك في بوت الأخوات الموحدات!")

# تشغيل البوت باستمرار
if __name__ == "__main__":
    print("البوت يعمل الآن...")
    bot.infinity_polling()
