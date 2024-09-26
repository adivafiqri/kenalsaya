import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import pandas as pd

# API key Telegram bot
api_key = '7330140742:AAEsQrY7d1M8chHAau0t_qvdG9S4oOf6b-k'
bot = telebot.TeleBot(api_key)

# Dictionary to hold the paths to each CSV file
csv_files = {
    'KSATRIA SADACARA - 24a': '24a.csv',
    'KSATRIA SATTWIKA - 23a': '23a.csv',
    'KSATRIA SATTWIKA - 23b': '23b.csv',
    'DHARMA CENDEKIA - 22': '22.csv',
    'KSATRIA CENDEKIA - 21': '21.csv'
}

# Placeholder for the currently selected DataFrame
selected_data = None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    for key in csv_files.keys():
        markup.add(InlineKeyboardButton(key.upper(), callback_data=f"select_{key}"))
    
    # Add Help button
    markup.add(InlineKeyboardButton("HELP", callback_data="help"))

    bot.reply_to(message, "Howdy! Pilih salah satu dataset berikut atau klik Help untuk informasi penggunaan:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_"))
def select_dataset(call):
    global selected_data
    selection = call.data.split("_")[1]  # Extract the dataset name from the callback data

    # Reset selected_data before loading the new dataset
    selected_data = None

    # Load the selected CSV into a DataFrame
    file_path = csv_files.get(selection)
    if file_path and os.path.exists(file_path):
        try:
            selected_data = pd.read_csv(file_path, delimiter=';', encoding='ISO-8859-1')
            bot.send_message(call.message.chat.id, f"Data {selection.upper()} telah dipilih! Sekarang ketik /cari 'NAMA' untuk mencari data.")
        except UnicodeDecodeError:
            bot.send_message(call.message.chat.id, f"Terjadi kesalahan saat membaca file {selection.upper()}. Pastikan file memiliki encoding yang benar.")
    else:
        bot.send_message(call.message.chat.id, "File CSV tidak ditemukan atau tidak dapat diakses.")

@bot.callback_query_handler(func=lambda call: call.data == "help")
def show_help(call):
    help_message = """
/start --> untuk memulai bot dan memilih dataset
/cari 'nama' --> untuk mencari data dalam dataset yang dipilih
/restart --> untuk merestart bot dan memilih dataset lain
/help --> untuk melihat informasi penggunaan
/end --> untuk mengakhiri bot
    """
    bot.send_message(call.message.chat.id, help_message)

@bot.message_handler(commands=['cari'])
def search_name_and_reply(message):
    global selected_data

    if selected_data is None:
        bot.reply_to(message, "Silakan pilih dataset terlebih dahulu dengan mengklik salah satu tombol.")
        return

    # Extract the name to search after the command
    search_text = message.text[len('/cari '):].strip().lower()

    if search_text:
        # Search for the name in the selected dataset
        matched_rows = selected_data[selected_data['NAMA'].str.lower().str.contains(search_text, na=False)]

        if not matched_rows.empty:
            for _, row in matched_rows.iterrows():
                reply_message = f"""
Siap, Senior.
Mohon izin menjawab, Senior.

Nama     : {row['NAMA']}
Dik Pol  : {row['DIKPOL']}
Pangkat  : {row['PANGKAT']}
NRP      : {row['NRP']}
Asal     : {row['ASAL']}
Prodi    : {row['PRODI']}
Alumni   : {row['ALUMNI']}
Satker   : {row['SATKER']}

Selanjutnya mohon petunjuk dan arahan. Terima kasih, Senior.
                """
                bot.reply_to(message, reply_message)
        else:
            bot.reply_to(message, "Nama tidak ditemukan.")
    else:
        bot.reply_to(message, "Tolong tulis nama setelah perintah /cari. contoh /cari 'Deka'")

@bot.message_handler(commands=['restart'])
def restart_bot(message):
    global selected_data
    selected_data = None  # Reset the selected data
    send_welcome(message)  # Call the send_welcome function to show the dataset options again

@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = """
/start --> untuk memulai bot dan memilih dataset
/cari 'nama' --> untuk mencari data dalam dataset yang dipilih
/restart --> untuk merestart bot dan memilih dataset lain
/help --> untuk melihat informasi penggunaan
/end --> untuk mengakhiri bot
    """
    bot.reply_to(message, help_message)

@bot.message_handler(commands=['end'])
def end_bot(message):
    bot.reply_to(message, "Bot dihentikan. Sampai jumpa!")
    # Optionally, stop the bot
    # bot.stop_polling()

print('bot berjalan')
bot.infinity_polling()
