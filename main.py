import logging
import requests
import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

BACK_TO_MENU, QUICKCOUNT, CANDIDATE, INFO, HOAX = range(5)

async def start(update: Update, context: ContextTypes):
    """Send a message when the command /start is issued."""
    user = update.message.from_user
    reply_keyboard = [["Quick Count", "Candidate"]]
    logger.info("User %s started the conversation.", user.first_name)
    await update.message.reply_text(
        "This handy bot parses data directly from the official <b>KPU (General Election Commission)</b> website, providing you with Quick-time updates on candidates, election results, and important announcements 📢.\n\n"
        "by <a href='https://github.com/1tte'>1tte</a>",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True), 
        parse_mode=ParseMode.HTML
    )

    
    return BACK_TO_MENU

async def quickcount(update: Update, context: ContextTypes):
    user = update.message.from_user
    reply_keyboard = [["Quick Count", "Candidate"]]
    response = requests.get("https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp.json")
    data = response.json()
    ts = data["ts"]
    result_data_01 = data["chart"]["100025"]
    result_data_02 = data["chart"]["100026"]
    result_data_03 = data["chart"]["100027"]
    persen = data["chart"]["persen"]
    progress_from_tps = data["progres"]["total"]
    progress_to_tps = data["progres"]["progres"]

    total = result_data_01 + result_data_02 + result_data_03

    percentage_01 = (result_data_01 / total) * 100
    percentage_02 = (result_data_02 / total) * 100
    percentage_03 = (result_data_03 / total) * 100

    logger.info("User %s started the conversation.", user.first_name)
    await update.message.reply_text(
        "<b>Quick Count</b>\n\n"
        "<b>Last Data</b>   : {}\n".format(ts) +
        "<b>Progress</b>    : {:,} / {} TPS ({}%)\n\n".format(progress_to_tps, progress_from_tps, persen).replace(",", ".") +
        "<b>Result Data and Percentage</b>\n" +
        "<b>01</b> : {:,} ({:.2f}%)\n".format(result_data_01, percentage_01).replace(",", ".") +
        "<b>02</b> : {:,} ({:.2f}%)\n".format(result_data_02, percentage_02).replace(",", ".") +
        "<b>03</b> : {:,} ({:.2f}%)\n\n".format(result_data_03, percentage_03).replace(",", ".") +

        "Total Incoming Votes: <b>{:,}</b>\n".format(total).replace(",", "."),
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        parse_mode=ParseMode.HTML
    )

    return BACK_TO_MENU

async def candidate(update: Update, context: ContextTypes):
    user = update.message.from_user
    reply_keyboard = [["Quick Count", "Candidate"]]
    response = requests.get("https://mul-co.com/wp-admin/x.json")
    data = response.json()
    candidates = data["candidates"]
    logger.info("User %s started the conversation.", user.first_name)

    message = ""
    for candidate in candidates:
        name = candidate["name"]
        position = candidate["position"]
        full_name = candidate["full_name"]
        birth_info_place = candidate["birth_info"]["place"]
        birth_date = candidate["birth_info"]["date"]
        age = candidate["age"]
        career = "\n".join(candidate["career"])

        message += (
            "<b>Name:</b> {}\n".format(name) +
            "<b>Position:</b> {}\n".format(position) +
            "<b>Full Name:</b> {}\n".format(full_name) +
            "<b>Birth Place:</b> {}\n".format(birth_info_place) +
            "<b>Birth Date:</b> {}\n".format(birth_date) +
            "<b>Age:</b> {}\n".format(age) +
            "<b>Career:</b>\n{}\n\n".format(career)
        )



    await update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        parse_mode=ParseMode.HTML,
    )
    
    image_path = r"cacawa.png"
    # Check if the file exists
    if os.path.exists(image_path):
        # Send the photo
        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=open(image_path, 'rb'),
            caption="Photo of the candidates."
        )
    else:
        # If the file doesn't exist, inform the user
        await update.message.reply_text("Sorry, the photo could not be found.")


    return BACK_TO_MENU


async def back_to_menu(update: Update, context: ContextTypes):
    """Show the menu."""
    user = update.message.from_user
    reply_keyboard = [["Quick Count", "Candidate"]]
    logger.info("User %s started the conversation.", user.first_name)
    await update.message.reply_text(
        "This handy bot parses data directly from the official <b>KPU (General Election Commission)</b> website, providing you with Quick-time updates on candidates, election results, and important announcements 📢.\n\n"
        "by <a href='https://github.com/1tte'>1tte</a>",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True), 
        parse_mode=ParseMode.HTML
    )

    return BACK_TO_MENU

def main():
    """Start the bot."""
    # Create the Application instance
    app = Application.builder().token("YOUR BOT TOKEN").build()

    # Get the dispatcher to register handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            BACK_TO_MENU: [
                MessageHandler(filters.Text("Quick Count"), quickcount),
                MessageHandler(filters.Text("Candidate"), candidate),
            ],
            QUICKCOUNT: [MessageHandler(filters.Text, back_to_menu)],
            CANDIDATE: [MessageHandler(filters.Text, back_to_menu)],

        },
        fallbacks=[CommandHandler("start", back_to_menu)],
    )

    app.add_handler(conv_handler)

    # Start the Bot
    app.run_polling()

if __name__ == "__main__":
    main()
