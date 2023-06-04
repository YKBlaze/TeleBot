import gspread
import re
from datetime import datetime
import coinaddrvalidator
from google.oauth2.service_account import Credentials
from email_validator import validate_email, EmailNotValidError

# Authenticate with the Google Sheets API
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
credentials = Credentials.from_service_account_file(
    #TODO ADD JSON
    #"telegramtestbot.json", scopes=scopes
)
client = gspread.authorize(credentials)

# Open the Google Spreadsheet
spreadsheet = client.open("<SpreadsheetNameTopLeft>")
worksheet_name = "<SpreadSheetNameTabBotLeft>"
worksheet = spreadsheet.worksheet(worksheet_name)

def get_ref_num():
    # Get the current available blank row number
    ref_num = None
    col_values = worksheet.col_values(1)  # Assuming column A is used to track empty rows

    for row_num in range(len(col_values), 0, -1):
        if not col_values[row_num - 1]:
            ref_num = row_num
            break

    if ref_num is None:
        ref_num = len(col_values) + 1
    print(f"{ref_num}")
    return ref_num - 1


from typing import Final
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Validate BTC and USDT addresses
def validate_wallet_address(address):
    result_btc = coinaddrvalidator.validate('btc', address)
    result_eth = coinaddrvalidator.validate('eth', address)
    # TODO Increase the amount of validations
    print(f"BTC: {result_btc.valid},\nETH: {result_eth.valid}")
    if result_btc.valid or result_eth.valid:
        return True
    else:
        return False



# Example usage
btc_address = "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2"
usdt_address = "0x89D24A7b4cCB1b6fAA2625fE562bDD9a23260359"
eth_address = "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4"



class InfoPerson:
    def __init__(self):
        self.date= ""
        self.name = ""
        self.email = ""
        self.exchange = ""
        self.wallet = ""
        self.hash = ""
        self.amount = ""
        self.currency = ""


infoPerson = InfoPerson()
TOKEN: Final = "<BotToken>"
BOT_USERNAME: Final = "@<BotUserName>"
#TODO GROUP_ID: Final = <Group ID>  # Replace with the ID of the specific group

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Type /create to reset the account details.\n"
    message += "Type /check to see account details so far\n"
    message += "Type /help to see how to edit account details\n"
    message += "Type /send to send info to spreadsheet"
    await update.message.reply_text(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Type the following commands to enter the corresponding information:\n"
    message += '- "date:01/01/01" to enter date\n'
    message += '- "name:username" to enter username\n'
    message += '- "email:EmailAddress" to enter email\n'
    message += '- "wallet:exchange" to enter exchange\n'
    message += '- "wallet:address" to enter wallet address\n'
    message += '- "hash:HashNumber" to enter hash\n'
    message += '- "amount:TheAmount" to enter amount\n'
    message += '- "amount:symbol" to enter currency\n\n'
    message += "Type /create to reset the account details.\n"
    message += "Type /check to see account details so far\n"
    message += "Type /help to see how to edit account details\n"
    message += "Type /send to send info to spreadsheet"
    await update.message.reply_text(message)


async def send_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if any(
        value == ""
        for value in [
            infoPerson.date,
            infoPerson.name,
            infoPerson.email,
            infoPerson.exchange,
            infoPerson.wallet,
            infoPerson.hash,
            infoPerson.amount,
            infoPerson.currency,
        ]
    ):
        await update.message.reply_text("One or more values are missing. Data not sent.")
        return

    # Write the information to the Google Spreadsheet
    row_data = [infoPerson.date, infoPerson.name, infoPerson.email, infoPerson.exchange, infoPerson.wallet, infoPerson.hash, infoPerson.amount,infoPerson.currency]
    worksheet.append_row(row_data)

    # Prepare the data string to display
    data_string = "\n".join(
        f"{key}: {value}"
        for key, value in zip(["Date", "Name", "Email", "Exchange", "Wallet", "Hash", "Amount","Currency"], row_data)
    )

    # Send the success message along with the data
    if int(infoPerson.amount) > 9999:
        success_message = f"🔥🔥🔥🔥🔥🔥🔥🔥{infoPerson.amount}{infoPerson.currency}🔥🔥🔥🔥🔥🔥🔥🔥\nData successfully added to the spreadsheet!\n\n{data_string}"
    else:
        success_message = f"✅✅✅✅✅{infoPerson.amount}{infoPerson.currency}✅✅✅✅✅\nData successfully added to the spreadsheet!\n\n{data_string}"


    # Send the success message to the group
    reference_number = get_ref_num()
    group_message = f"{success_message}\n\nReference Number: {reference_number}"
    

    # Send the success message and quote it
    success_quote = await update.message.reply_text(group_message, quote=True)

    await context.bot.send_message(chat_id=GROUP_ID, text=group_message)
    

    # Send the "😍" response as a quote to the success message
    if int(infoPerson.amount) > 10000:
         response_message = "🎆🎆💥💥🔥🔥🧨😍🧨🔥🔥💥💥🎆🎆"  # Create the response message with "😍"
         await success_quote.reply_text(response_message, quote=True)
    

    # Reset infoPerson values
    infoPerson.date = ""
    infoPerson.name = ""
    infoPerson.email = ""
    infoPerson.exchange = ""
    infoPerson.wallet = ""
    infoPerson.hash = ""
    infoPerson.amount = ""
    infoPerson.currency = ""


async def create_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    infoPerson.date = ""
    infoPerson.name = ""
    infoPerson.email = ""
    infoPerson.exchange = ""
    infoPerson.wallet = ""
    infoPerson.hash = ""
    infoPerson.amount = ""
    infoPerson.currency = ""
    await update.message.reply_text("Type /help to view commands")


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = f"Current Data:\n" + '\n'.join(f"{key.capitalize()}: {value}" for key, value in infoPerson.__dict__.items())
    await update.message.reply_text(response)



def handle_response(text: str) -> str:
    lines = text.split("\n")
    data = {}

    # Process each line and extract key-value pairs
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)  # Split only once
            key = key.strip()
            value = value.strip()
            if key == "wallet":
                data[key] = value  # Preserve capital letters in the wallet value
            else:
                data[key.lower()] = value.lower()  # Convert other keys and values to lowercase

    # Validate and assign the data to infoPerson
    if "date" in data:
        date = data["date"]
        try:
                datetime.strptime(date, "%d/%m/%y")
                infoPerson.date = date
        except ValueError:
                return "Invalid date format. Please provide a date in the format dd/mm/yy"

    if "name" in data:
        name = data["name"]
        if len(name) > 30:
            return "Name cannot be longer than 30 characters."
        if re.search(r"\d", name):
            return "Name cannot contain numbers."
        # Capitalize the first letter of every word
        name = " ".join(word.capitalize() for word in name.split())
        infoPerson.name = name

    if "email" in data:
        email = data["email"]
        try:
            # Validate the email
            validate_email(email)
            infoPerson.email = email
        except EmailNotValidError:
            return "Invalid email. Please provide a valid email address."
        
    if "exchange" in data:
        exchange = data["exchange"]
        exchange = exchange.capitalize()
        infoPerson.exchange = exchange

    if "wallet" in data:
        wallet_value = data["wallet"]
        if not validate_wallet_address(wallet_value):
            return "Invalid wallet address."
        infoPerson.wallet = wallet_value

    if "hash" in data:
        hash_value = data["hash"]
        infoPerson.hash = hash_value

    if "amount" in data:
        amount = data["amount"]
        if not re.match(r"^\d+$", amount) or int(amount) <= 0:
            return "Invalid amount. Amount must be a positive number."
        infoPerson.amount = amount
    
    if "currency" in data:
        currency = data["currency"].upper()
        infoPerson.currency = currency

    if "🐓" in data:
        return f"🐓🐓🐓🐔🐔🐔🐔🐔🐓🐓🐓🐓"
    
    # Check if no data was assigned
    if not infoPerson.name and not infoPerson.email and not infoPerson.hash and not infoPerson.amount and not infoPerson.currency and not infoPerson.date:
        return "I didn't understand. Type /help for more info"

    return "Current Data:\n" + '\n'.join(f"{key.capitalize()}: {value}" for key, value in infoPerson.__dict__.items())




async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get basic info of the incoming message
    if update.message is None:
        return  # Ignore the update if there is no message
    
    message_type: str = update.message.chat.type
    text: str = update.message.text

    # Print a log for debugging
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    # React to group messages only if users mention the bot directly
    if message_type == 'supergroup':
        # Replace with your bot username
        if BOT_USERNAME in text:
            # new_text: str = text.replace(BOT_USERNAME, '').strip()
            # response: str = handle_response(new_text)
            return
        else:
            return  # We don't want the bot respond if it's not mentioned in the group
    else:
        response: str = handle_response(text)

    # Reply normally if the message is in private
    print('Bot:', response)
    await update.message.reply_text(response)



async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("send", send_command))
    app.add_handler(CommandHandler("check", check_command))  # Add check_command handler
    app.add_handler(CommandHandler("create", create_command))  # Add check_command handler

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print("Polling...")
    app.run_polling(poll_interval=3)
