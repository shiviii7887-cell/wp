import os
import logging
import requests
import httpx
from telegram.ext import CallbackQueryHandler
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest

# ========== CONFIG ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")
VEHICLE_API = "https://sbsakib.eu.cc/apis/vehicle_advance?key=Demo&rc="
PINCODE_API = "https://sbsakib.eu.cc/apis/pincode_info?key=Demo&pincode="
IFSC_API    = "https://sbsakib.eu.cc/apis/ifsc_info?key=Demo&ifsc="
IP_API      = "https://sbsakib.eu.cc/apis/ip_info?key=Demo&ip="
CH1_LINK = os.getenv("CH1_LINK")
CH1_LINK = "https://t.me/ruchika_ownss"


# ── Join Check ───────────────────────────────────────────────────────────────

async def is_user_joined(bot, user_id):
    try:
        mem1 = await bot.get_chat_member(CH1_ID, user_id)
        ch1 = mem1.status not in ['left', 'kicked']
                
        return ch1
    except Exception as e:
        print(f"Join check error: {e}")
        return True

def get_join_message(user_name):
    text = (
        f"Hey {user_name} 👋\n\n"
        "Please Join All My Update Channels To Use Me! 🔒"
    )
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 Join Channel 1", url=CH1_LINK)
            
        ],
        [InlineKeyboardButton("♻️ Try Again", callback_data="verify_join")],
    ])
    return text, markup

# ── Decorator for join check ─────────────────────────────────────────────────

def require_join(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        joined = await is_user_joined(context.bot, user.id)
        if not joined:
            user_name = user.first_name or "User"
            text, markup = get_join_message(user_name)
            await update.message.reply_text(text, reply_markup=markup)
            return
        return await func(update, context)
    wrapper.__name__ = func.__name__
    return wrapper

# ── Callback: Verify Join ────────────────────────────────────────────────────

async def verify_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    joined = await is_user_joined(context.bot, user.id)

    if joined:
        await query.answer("☬ ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ ᴄᴏᴍᴘʟᴇᴛᴇ ☬\n🔓 ᴀᴄᴄᴇss ɢʀᴀɴᴛᴇᴅ", show_alert=True)
        try:
            await query.message.delete()
        except:
            pass
        success = (
            "┏━━━「 ᴀᴄᴄᴇss ɢʀᴀɴᴛᴇᴅ 🎉 」━━━┓\n"
            "┃\n"
            "┃ 🔓 *ʙᴏᴛ sᴜᴄᴄᴇssғᴜʟʟʏ ᴜɴʟᴏᴄᴋᴇᴅ!*\n"
            "┃\n"
            "┃ 👉 Type /start to begin!\n"
            "┃\n"
            "┗━━━━━━━━━━━━━━━━━━━━┛"
        )
        await context.bot.send_message(query.message.chat.id, success, parse_mode="Markdown")
    else:
        await query.answer("❌ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ғᴀɪʟᴇᴅ • ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟs ғɪʀsᴛ", show_alert=True)

# ============================

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

@require_join
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 *LOOKUP INFO BOT*\n\n"

        "📱 Number Lookup: `/num 9876543210`\n"
        "📱 TG Lookup: `/tg 4589174428`\n"
        "🪪 Aadhaar Lookup: `/aadhar 54958327738`\n"
        "💳 UPI Info: `/upi username@paytm`\n"
        "🚗 Vehicle RC: `/rc DL10CA7539`\n"
        "📮 Pincode Info: `/pin 110001`\n"
        "🏦 IFSC Info: `/ifsc SBIN0004843`\n"
        "🌐 IP Info: `/ip 8.8.8.8`\n\n"

        "⚠️ Some services are currently under maintenance.",
        parse_mode="Markdown"
    )

async def num_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Number daal!\nExample: `/num 9876543210`", parse_mode="Markdown")
        return

    number = context.args[0].strip().replace("+","").replace(" ","").replace("-","")
    if not number.isdigit() or len(number) < 8:
        await update.message.reply_text("❌ Valid number daal (sirf digits)!")
        return

    await update.message.reply_text(
        f"📱 *Number:* `{number}`\n\n"
        "🔍 Is number ki info ke liye owner se contact karo:\n"
        "👉 @ruchika\\_owns",
        parse_mode="Markdown"
    )

async def rc_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ RC number daal!\nExample: `/rc DL10CA7539`", parse_mode="Markdown")
        return

    rc = context.args[0].strip().upper()
    msg = await update.message.reply_text(f"🔍 Fetching vehicle info for `{rc}`...", parse_mode="Markdown")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{VEHICLE_API}{rc}")
            d = resp.json()

        if not d.get("success"):
            await msg.edit_text(f"❌ {d.get('message', 'Not found')}")
            return

        data = d["data"]
        o = data["owner_details"]
        v = data["vehicle_details"]
        ins = data["insurance_details"]
        dates = data["important_dates"]
        rto = data["rto_details"]

        text = (
            f"🚗 *Vehicle: {data['registration_number']}*\n\n"
            f"👤 *Owner*\n• Name: `{o['owner_name']}`\n• Address: {o['present_address'].strip()}\n• RTO: {o['registered_rto']}\n\n"
            f"🏎️ *Vehicle*\n• {data['make_brand']} {data['model_name_v2']}\n• Color: {data['vehicle_color']}\n• Fuel: {v['fuel_type']} | CC: {v['cubic_capacity']}\n\n"
            f"📅 *Dates*\n• Registered: {dates['registration_date']}\n• Age: {dates['vehicle_age']}\n• Fitness: {dates['fitness_upto']} | Tax: {dates['tax_upto']}\n\n"
            f"🛡️ *Insurance*\n• {ins['status']}\n• {ins['insurance_company']} | Upto: {ins['insurance_upto']}\n\n"
            f"🏢 *RTO*\n• {rto['city']} ({rto['code']}) 📞 {rto['phone']}"
        )
        await msg.edit_text(text, parse_mode="Markdown")
    except httpx.TimeoutException:
        await msg.edit_text("⏳ Timeout! Thodi der baad try kar.")
    except Exception as e:
        import traceback; traceback.print_exc()
        await msg.edit_text(f"❗ Error:\n{str(e)}")

async def pin_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Pincode daal!\nExample: `/pin 110001`", parse_mode="Markdown")
        return

    pincode = context.args[0].strip()
    if not pincode.isdigit() or len(pincode) != 6:
        await update.message.reply_text("❌ Valid 6-digit pincode daal!")
        return

    msg = await update.message.reply_text(f"🔍 Fetching pincode info for `{pincode}`...", parse_mode="Markdown")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{PINCODE_API}{pincode}")
            d = resp.json()

        if d.get("Status") != "Success":
            await msg.edit_text("❌ Pincode not found!")
            return

        offices = d.get("PostOffice", [])
        first = offices[0]
        names = ", ".join([o["Name"] for o in offices])

        text = (
            f"📮 *Pincode: {pincode}*\n\n"
            f"• *State:* {first.get('State','N/A')}\n"
            f"• *District:* {first.get('District','N/A')}\n"
            f"• *Division:* {first.get('Division','N/A')}\n"
            f"• *Region:* {first.get('Region','N/A')}\n"
            f"• *Block:* {first.get('Block','N/A')}\n"
            f"• *Country:* {first.get('Country','N/A')}\n\n"
            f"🏤 *Post Offices ({len(offices)}):*\n{names}"
        )
        if len(text) > 4096:
            text = text[:4090] + "..."
        await msg.edit_text(text, parse_mode="Markdown")
    except httpx.TimeoutException:
        await msg.edit_text("⏳ Timeout! Thodi der baad try kar.")
    except Exception as e:
        import traceback; traceback.print_exc()
        await msg.edit_text(f"❗ Error:\n{str(e)}")

async def ifsc_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ IFSC daal!\nExample: `/ifsc SBIN0004843`", parse_mode="Markdown")
        return

    ifsc = context.args[0].strip().upper()
    msg = await update.message.reply_text(f"🔍 Fetching IFSC info for `{ifsc}`...", parse_mode="Markdown")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{IFSC_API}{ifsc}")
            d = resp.json()

        if "BANK" not in d:
            await msg.edit_text("❌ IFSC not found!")
            return

        text = (
            f"🏦 *IFSC: {ifsc}*\n\n"
            f"• *Bank:* {d.get('BANK','N/A')}\n"
            f"• *Branch:* {d.get('BRANCH','N/A')}\n"
            f"• *City:* {d.get('CITY','N/A')}\n"
            f"• *District:* {d.get('DISTRICT','N/A')}\n"
            f"• *State:* {d.get('STATE','N/A')}\n"
            f"• *Address:* {d.get('ADDRESS','N/A')}\n"
            f"• *Contact:* {d.get('CONTACT') or 'N/A'}\n"
            f"• *MICR:* {d.get('MICR','N/A')}\n"
            f"• *NEFT:* {'✅' if d.get('NEFT') else '❌'}  "
            f"*RTGS:* {'✅' if d.get('RTGS') else '❌'}  "
            f"*IMPS:* {'✅' if d.get('IMPS') else '❌'}  "
            f"*UPI:* {'✅' if d.get('UPI') else '❌'}"
        )
        await msg.edit_text(text, parse_mode="Markdown")
    except httpx.TimeoutException:
        await msg.edit_text("⏳ Timeout! Thodi der baad try kar.")
    except Exception as e:
        import traceback; traceback.print_exc()
        await msg.edit_text(f"❗ Error:\n{str(e)}")

async def ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ IP daal!\nExample: `/ip 8.8.8.8`", parse_mode="Markdown")
        return

    ip = context.args[0].strip()
    msg = await update.message.reply_text(f"🔍 Fetching IP info for `{ip}`...", parse_mode="Markdown")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{IP_API}{ip}")
            d = resp.json()

        if d.get("response_code") != "200":
            await msg.edit_text("❌ IP not found or invalid!")
            return

        text = (
            f"🌐 *IP Info: {d.get('ip', ip)}*\n\n"
            f"• *Country:* {d.get('country_name','N/A')} ({d.get('country_code2','N/A')})\n"
            f"• *ISP:* {d.get('isp','N/A')}\n"
            f"• *IP Version:* IPv{d.get('ip_version','N/A')}"
        )
        await msg.edit_text(text, parse_mode="Markdown")
    except httpx.TimeoutException:
        await msg.edit_text("⏳ Timeout! Thodi der baad try kar.")
    except Exception as e:
        import traceback; traceback.print_exc()
        await msg.edit_text(f"❗ Error:\n{str(e)}")

async def maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠️ Bot Under Maintenance\n\n"
        "For any update related bot:\n"
        "contact owner @ruchika_owns"
    )

def main():
    request = HTTPXRequest(connect_timeout=30, read_timeout=60, write_timeout=60, pool_timeout=30)
    app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", start))
    
    app.add_handler(CommandHandler("num", maintenance))
    app.add_handler(CommandHandler("rc", maintenance))
    app.add_handler(CommandHandler("pin", maintenance))
    app.add_handler(CommandHandler("ifsc", maintenance))
    app.add_handler(CommandHandler("ip", maintenance))
    app.add_handler(CommandHandler("tg", maintenance))
    app.add_handler(CommandHandler("aadhar", maintenance))
    app.add_handler(CommandHandler("upi", maintenance))

    app.add_handler(
        CallbackQueryHandler(
            verify_join_callback,
            pattern="verify_join"
        )
    )


    print("=" * 50)
    print("Bot chal raha hai...")
    print("=" * 50)
    app.run_polling()

if __name__ == "__main__":
    main()
