import os
import telebot
from telebot import types
from datetime import datetime
import pytz
from hijri_converter import Gregorian
from apscheduler.schedulers.background import BackgroundScheduler

# جلب توكن البوت بشكل آمن من بيئة تشغيل Railway
TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# تحديد التوقيت الجزائري كمنطقة زمنية افتراضية للبوت
ALGERIA_TZ = pytz.timezone('Africa/Algiers')

# قائمة لتخزين معرفات شات المستخدمين لإرسال التذكيرات التلقائية
SUBSCRIBED_USERS = set()

# ==================== قاعدة بيانات البوت (محتوى المكتبة) ====================

AZKAR = {
    "sabah": (
        "☀️ *أذكار الصباح كاملة للتحصين:*\n\n"
        "1️⃣ «أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَهَ إِلَّا اللهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ»\n\n"
        "2️⃣ «اللَّهُمَّ بِكَ أَصْبَحْنَا، وَبِكَ أَمْسَيْنَا، وَبِكَ نَحْيَا، وَبِكَ نَمُوتُ، وَإِلَيْكَ النُّشُورُ»\n\n"
        "3️⃣ «اللَّهُمَّ أَنْتَ رَبِّي لَا إِلَهَ إِلَّا أَنْتَ، خَلَقْتَنِي وَأَنَا عَبْدُكَ، وَأَنَا عَلَى عَهْدِكَ وَوَعْدِكَ مَا اسْتَطَعْتُ، أَعُوذُ بِكَ مِنْ شَرِّ مَا صَنَعْتُ، أَبُوءُ لَكَ بِنِعْمَتِكَ عَلَيَّ، وَأَبُوءُ لَذَنْبِي فَاغْفِرْ لِي فَإِنَّهُ لَا يَغْفِرُ الذُّنُوبَ إِلَّا أَنْتَ»\n\n"
        "4️⃣ قراءة آية الكرسي، وسورة الإخلاص والمعوذتين (3 مرات)."
    ),
    "masa": (
        "🌙 *أذكار المساء كاملة للتحصين:*\n\n"
        "1️⃣ «أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَهَ إِلَّا اللهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ»\n\n"
        "2️⃣ «اللَّهُمَّ بِكَ أَمْسَيْنَا، وَبِكَ أَصْبَحْنَا، وَبِكَ نَحْيَا، وَبِكَ نَمُوتُ، وَإِلَيْكَ الْمَصِيرُ»\n\n"
        "3️⃣ «أَعُوذُ بِكَلِمَاتِ اللهِ التَّامَّاتِ مِنْ شَرِّ مَا خَلَقَ» (3 مرات).\n\n"
        "4️⃣ «بِسْمِ اللَّهِ الَّذِي لَا يَضُرُّ مَعَ اسْمِهِ شَيْءٌ فِي الْأَرْضِ وَلَا فِي السَّمَاءِ وَهُوَ السَّمِيعُ الْعَلِيمُ» (3 مرات)."
    )
}

SHARIA_SCIENCES = {
    "aqeedah": (
        "💎 *قسم العقيدة والتوحيد الخالص:*\n\n"
        "• *أصل الدين وأساسه:* هو تحقيق التوحيد وإفراد الله بالعبادة، والكفر بكل طاغوت يُعبد من دون الله تبارك وتعالى.\n\n"
        "• *شروط لا إله إلا الله:* العلم، اليقين، القبول، الانقياد، الصدق، الإخلاص، والمحبة.\n\n"
        "• *نواقض الإسلام:* ينبغي للموحد معرفتها للحذر منها، وأعظمها الشرك في عبادة الله، ومظاهرة المشركين ومعاونتهم على المسلمين."
    ),
    "fiqh": (
        "🕌 *قسم الفقه المستنير وأحكام الديار:*\n\n"
        "• *فقه العبادات:* فرض عين معرفة أحكام الطهارة، والصلوات الخمس بشروطها وأركانها لأنها عمود الدين.\n\n"
        "• *فقه الرباط والثغور:* فضل الرباط في سبيل الله وعظيم أجر الصابرين والمحتسبين في ثغور المسلمين للدفاع عن بيضة الدين.\n\n"
        "• *فقه الأسرة المسلمة:* تربية أشبال الموحدين على مائدة الكتاب والسنة، وحث الأخوات على الصبر والاحتساب في غياب غزاة المسلمين."
    ),
    "hadith": (
        "💬 *قسم الحديث الشريف والسنة النبوية:*\n\n"
        "• *التمسك بالأثر:* قال رسول الله ﷺ: «عَلَيْكُمْ بِسُنَّتِي وَسُنَّةِ الْخُلَفَاءِ الرَّاشِدِينَ الْمَهْدِيِّينَ عَضُّوا عَلَيْهَا بِالنَّوَاجِذِ».\n\n"
        "• *كتب السنة:* يُنصح الموحد بمدارسة (الأربعين النووية) أولاً لفهم أصول جوامع الكلم، ثم التوسع في صحيحي البخاري ومسلم."
    )
}

HISTORICAL_EVENTS = {
    "1": "📅 معركة اليرموك الخالدة بقيادة سيف الله المسلول خالد بن الوليد وتحطيم إمبراطورية الروم.",
    "2": "📅 فتح مدائن كسرى عاصمة الفرس وسقوط إمبراطورية المجوس تحت أقدام الفاتحين الموحدين.",
    "3": "📅 غزوة بدر الكبرى (يوم الفرقان) أعز الله فيها القلة المؤمنة وكسر شوكة طواغيت قريش.",
    "4": "📅 عبور الفاتح طارق بن زياد وموسى بن نصير وبدء الفتح الإسلامي للأندلس وغرس التوحيد فيها.",
    "5": "📅 فتح القسطنطينية وتحقيق بشارة النبي ﷺ الخالدة على يد السلطان الشاب محمد الفاتح وجنده.",
    "6": "📅 غزوة خيبر المباركة وإخضاع حصون اليهود المنيعة ورفع راية الإسلام بيد علي بن أبي طالب.",
    "7": "📅 معركة حطين الخالدة بقيادة الناصر صلاح الدين الأيوبي وتدمير الصليبيين وتحرير بيت المقدس.",
    "8": "📅 معركة ملاذكرد الشهيرة بقيادة السلطان ألب أرسلان ونصر جند المسلمين على جحافل الروم.",
    "9": "📅 معركة عين جالوت المباركة بقيادة سيف الدين قطز وكسر زحف التتار وحماية ديار الإسلام.",
    "10": "📅 معركة بلاط الشهداء في عمق الأراضي الفرنسية وثبات جيوش المسلمين بقيادة عبد الرحمن الغافقي.",
    "11": "📅 فتح القادسية العظيم بقيادة سعد بن أبي وقاص رضي عنه وهدم عروش الفرس الفانية في العراق.",
    "12": "📅 فتح مكة المكرمة (الفتح الأعظم) ودخول الناس في دين الله أفواجاً وتطهير البيت من الأصنام."
}

# ==================== الدوال المساعدة للمعلومات المتغيرة ====================

def get_date_message():
    now = datetime.now(ALGERIA_TZ)
    gregorian_str = now.strftime("%Y-%m-%d م")
    try:
        hijri = Gregorian(now.year, now.month, now.day).to_hijri()
        hijri_str = f"{hijri.day} {hijri.month_name()} {hijri.year} هـ"
    except Exception:
        hijri_str = "تعذر حساب التاريخ الهجري حالياً"
    
    return f"📅 *تاريخ اليوم ونفحات الوقت (بتوقيت الجزائر):*\n🔹 التاريخ الميلادي: {gregorian_str}\n🔸 التاريخ الهجري: {hijri_str}"

def get_jehad_dua():
    return (
        "⚔️ *دعاء الثبات والنصرة لأهل الثغور والجهاد:*\n\n"
        "«اللَّهُمَّ انْصُرْ عِبَادَكَ الْمُجَاهِدِينَ فِي سَبِيلِكَ فِي كُلِّ مَكَانٍ، اللَّهُمَّ سَدِّدْ رَمْيَهُمْ، وَثَبِّتْ أَقْدَامَهُمْ، وَأَفْرِغْ عَلَيْهِمْ صَبْراً، وَتَقَبَّلْ شُهَدَاءَهُمْ».\n\n"
        "📜 *دعاء خاص ومخلص لصاحبة هذا البوت القرآني:*\n"
        "«اللَّهُمَّ احْفَظْ عَبْدَكَ الْمُجَاهِدَ فِي جَزِيرَةِ مُحَمَّدٍ ﷺ، وَكُنْ لَهُ عَوْناً وَنَصِيراً وَمُعِيناً، وَتَقَبَّلْ رِبَاطَهُ وَجِهَادَهُ وَخُطَاهُ. "
        "اللَّهُمَّ ارْبِطْ عَلَى قَلْبِ زَوْجَتِهِ *الأُخْتِ الأَنْدَلُسِيَّةِ الصَّابِرَةِ* عَلَى غِيَابِهِ وَبُعْدِهِ نُصْرَةً لِدِينِكَ، وَآجِرْهَا فِي غُرْبَتِهَا وَصَبْرِهَا، وَأَعْظِمْ لَهَا الثَّوَابَ. "
        "اللَّهُمَّ احْفَظْ لَهَا ابْنَتَهَا وَحِيدَتَهَا، وَأَنْبِتْهَا نَبَاتاً حَسَناً بَارّاً طَائِعاً، وَاجْعَلْهَا مِنْ حَافِظَاتِ كِتَابِكَ، وَاجْمَعْ شَمْلَهُمْ سَرِيعاً غَيْرَ بَعِيدٍ عَلَى عِزٍّ وَتَمْكِينٍ فِي الدُّنْيَا وَالآخِرَةِ.. اللَّهُمَّ آمِينَ»."
    )

# ==================== صياغة لوحات التحكم ====================

def main_menu_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("✨ أذكار اليوم للتحصين", callback_data="menu_azkar")
    btn2 = types.InlineKeyboardButton("📚 العلوم الشرعية", callback_data="menu_sharia")
    btn3 = types.InlineKeyboardButton("📅 التقويم والحدث التاريخي", callback_data="menu_date")
    btn4 = types.InlineKeyboardButton("⚔️ دعاء الأخت الأندلسية", callback_data="menu_dua")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup

# ==================== التعامل مع الأوامر المباشرة ====================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    SUBSCRIBED_USERS.add(message.chat.id)
    
    welcome_text = (
        "🕌 *مرحباً بكم في مكتبة الموحدين والموحدات العلمية الشاملة*\n\n"
        "مرحباً بكِ أختي الغالية الصابرة، ومرحباً بك أخي الكريم الموحد.\n\n"
        "📢 *تم تفعيل جميع التنبيهات التلقائية لك يومياً بالتوقيت الجزائري:*\n"
        "• 🌌 قيام الليل (02:00 ليلاً)\n"
        "• ☀️ أذكار الصباح (06:00 صباحاً)\n"
        "• ⚔️ دعاء الأخت الأندلسية (09:00 صباحاً)\n"
        "• 🌙 أذكار المساء (17:00 مساءً)\n\n"
        "🔹 تصفح الأقسام وتنقّل بمرونة عبر الأزرار الشفافة أدناه:"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

# ==================== معالجة ضغطات الأزرار الشفافة ====================

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data

    if data == "main_menu":
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🔹 تصفح الأقسام وتنقّل بمرونة عبر الأزرار الشفافة أدناه:", parse_mode="Markdown", reply_markup=main_menu_keyboard())

    elif data == "menu_azkar":
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_sabah = types.InlineKeyboardButton("☀️ أذكار الصباح", callback_data="azkar_sabah")
        btn_masa = types.InlineKeyboardButton("🌙 أذكار المساء", callback_data="azkar_masa")
        btn_back = types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")
        markup.add(btn_sabah, btn_masa)
        markup.add(btn_back)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="✨ *اختر الأذكار المباركة لحفظك ووقتك:*", parse_mode="Markdown", reply_markup=markup)

    elif data in ["azkar_sabah", "azkar_masa"]:
        key = "sabah" if data == "azkar_sabah" else "masa"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 العودة لقسم الأذكار", callback_data="menu_azkar"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=AZKAR[key], parse_mode="Markdown", reply_markup=markup)

    elif data == "menu_sharia":
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_aqeedah = types.InlineKeyboardButton("💎 العقيدة والتوحيد", callback_data="sharia_aqeedah")
        btn_fiqh = types.InlineKeyboardButton("🕌 الفقه المستنير وأحكام الديار", callback_data="sharia_fiqh")
        btn_hadith = types.InlineKeyboardButton("💬 الحديث الشريف والسنة", callback_data="sharia_hadith")
        btn_back = types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")
        markup.add(btn_aqeedah, btn_fiqh, btn_hadith, btn_back)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="📚 *اختر المبحث العلمي الشرعي الذي تود تصفحه وفهمه:*", parse_mode="Markdown", reply_markup=markup)

    elif data.startswith("sharia_"):
        key = data.split("_")[1]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 العودة لقسم العلوم الشرعية", callback_data="menu_sharia"))
