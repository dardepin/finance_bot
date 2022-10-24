#!/usr/bin/env python
# pylint: disable=C0116,W0613

import logging;
from datetime import datetime;
import sqlite3;
from sqlite3 import Error
from calendar import monthrange;
import prettytable;

from telegram import Update, ForceReply, ParseMode;
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext;

from finance_bot_config import *;

logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)
logger = logging.getLogger(__name__)

def get_amount(amount, update: Update):

    try: amount_f =  float(amount.replace(',', '.'));
    except ValueError: update.message.reply_text(fr'Сумма должна быть в формате 100.1');
    return amount_f;

def get_sep(datestr):
    for sep in('.', ',', '-', '/'):
        if sep in datestr:
            return sep;
    return '';

def parse_date(update: Update, date): #parse date. return (date) or (date1, date2)

    if(date == ''): today = [datetime.now().replace(hour = 0, minute = 0, second = 0, microsecond = 0)];
    else:
        sep = get_sep(date);
        if(sep == ''): update.message.reply_text(fr'Неверный формат даты'); return None;
        try:
            seps = date.count(sep);
            #normal date
            if(seps == 2): today = [datetime.strptime(date, '%d' + sep + '%m' + sep + '%Y')];
            #month (10.22?)
            elif(seps == 1): today = get_dates(update, date, sep);
            else: update.message.reply_text(fr'Неверный формат даты'); return None;
        except:
            update.message.reply_text(fr'Неверный формат даты'); return None;

    return today;

def get_dates(update: Update, date, sep): #retn (date1, date2) or None

    month = date.split(sep)[0]; year = date.split(sep)[1]; #month and year
    lastday = monthrange(int(year), int(month))[1];

    try:
        dates = [datetime.strptime('1.' + month + '.' + year, '%d.%m.%Y'),
    datetime.strptime(str(lastday) + '.' + month + '.' + year, '%d.%m.%Y')];
    except Exception as e:
        update.message.reply_text(fr'Неверный формат даты: ' + str(e)); return None;

    return dates;

def get_date(update: Update, date): #parsing date or return '' as error

    if(date == ''): today = datetime.now().replace(hour = 0, minute = 0, second = 0, microsecond = 0);
    else:
        sep = get_sep(date);
        if(sep == ''): update.message.reply_text(fr'Неверный формат даты'); return None;
        try:
            today = datetime.strptime(date, '%d' + sep + '%m' + sep + '%Y');
        except:
            update.message.reply_text(fr'Неверный формат даты'); return None;
        
    return today;

def checkuser(update: Update, context: CallbackContext): #return True if user id in allowed user's list
    userid = update.effective_user.id;
    if(not userid or userid not in USERS):
        update.message.reply_text(fr'Не могу опознать пользователя по id:' +  str(userid) + fr'. Если вы админинстратор, то можете добавить этот id в переменную USRES');
        return False;
    return True;

def start(update: Update, context: CallbackContext) -> None:
    if(not checkuser(update, context)):
        return;
    else:
        username = update.effective_user.first_name + ' ' + update.effective_user.last_name;
        update.message.reply_text(fr'Привет, ' + str(username) + fr'!');
    return;

def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("""
    Доступные команды:
    /start Запускает бота и показывает, можете ли вы использовать бота. Еще вы можете узнать id своего пользователя с помощью этой команды.
    /help  Показывает это сообщение.
    отчет [дата] [категория] Показывает пополнения и затраты на текущую дату (если даты нет), либо на определенный день (если дата в формате '20.10.2022'), либо на текущий месяц (если дата имеет формат '10.2022').
    + сумма [дата] [категория] Добавляет запись о пополнении бюджета. Если дата в формате '20.10.2022' пропущена, то запись будет текущим числом. Если категория отсутствует, то категория будет 'Прочие'.
    - сумма [дата] [категория] Добавляет запись о списания из бюджета. Если дата в формате '20.10.2022' пропущена, то запись будет текущим числом. Если категория пропущена, то категория будет 'Прочие'.""");

def query_db(update: Update, context: CallbackContext, query, params = ''):

    сon = None;
    try:
        con = sqlite3.connect(DB_PATH);
        cur = con.cursor();
        if(params == ''): cur.execute(query);
        else: cur.execute(query, params);
        con.commit();

    except Error as e: update.message.reply_text(fr'SQLite error in query_db: ' + e); return False;
    finally:
        if con: con.close();
    return True;

def fetch_db(update: Update, context: CallbackContext, query, params = ''):

    сon = None;
    try:
        con = sqlite3.connect(DB_PATH);
        cur = con.cursor();
        if(params == ''): cur.execute(query);
        else: cur.execute(query, params);
        rows = cur.fetchall();

    except Error as e: update.message.reply_text(fr'SQLite error in fetch_db: ' + e); return None;
    finally:
        if con: con.close();
    return rows;

def create_db():

    con = None;
    query = 'CREATE TABLE IF NOT EXISTS operations (\'id\' INTEGER PRIMARY KEY, \'sign\' INTEGER NOT NULL, \'amount\' REAL NOT NULL, \'op_date\' timestamp NOT NULL, \'category\' TEXT NOT NULL)';

    try:
        con = sqlite3.connect(DB_PATH);
        cur = con.cursor();
        cur.execute(query);
        con.commit();
    except Error as e: print(fr'SQLite error in create_db: ' + e); return False;
    finally:
        if con: con.close();
    return True;

def topup_db(sign, amount, update: Update, context: CallbackContext, date = '', category = ''):

    amount = get_amount(amount, update);
    if(amount == 0.0): return;

    date_obj = get_date(update, date);
    if(date_obj == None): return;

    if(category == ''): category = 'Прочие';
    operation = "Доход: " if sign else "Расход: ";

    update.message.reply_text(operation + str(amount) + fr'; Дата: ' +  date_obj.strftime('%d.%m.%Y') + fr'; Категория: ' + category);

    query = 'INSERT INTO operations (sign, amount, op_date, category) VALUES (?, ?, ?, ?)';
    params = (sign, amount, date_obj, category);
    query_db(update, context, query, params);
    return;

def print_db(update: Update, context: CallbackContext, rows):

    idx = 1;
    table = prettytable.PrettyTable(['#', 'Номер', 'Дата', 'Тип', 'Сумма', 'Категория']);
    table.align['#'] = 'l';
    table.align['Номер'] = 'r';
    table.align['Дата'] = 'l';
    table.align['Тип'] = 'l';
    table.align['Сумма'] = 'l';
    table.align['Категория'] = 'l';

    #for idx, row in enumerate(rows):
        #data.append([idx, row[0], row[1], row[2], row[3], row[4]]);
    #for idx, number, date, type, category in data:
         #table.add_row([idx, f'{number:.2f}', f'{date:.3f}', f'{type:.4f}', f'{category:.5f}']);
    for idx, row in enumerate(rows):
        type = "Пополнение" if row[1] else "Трата";
        table.add_row([idx + 1, row[0], row[3], type, row[2], row[4]]);
    update.message.reply_text(f'<pre>{table}</pre>', parse_mode = ParseMode.HTML);

    return;

def rept_db(update: Update, context: CallbackContext, date = '', category = ''):

    dates = parse_date(update, date);
    if(dates == None): return;

    query = 'SELECT * FROM operations WHERE op_date '
    if(len(dates) == 1): query += '= \'' + dates[0].strftime('%Y-%m-%d %H:%M:%S') + '\'';
    elif(len(dates) == 2): query += 'BETWEEN \'' + dates[0].strftime('%Y-%m-%d %H:%M:%S') + '\' AND \'' + dates[1].strftime('%Y.%m.%d %H:%M:%S') + '\'';
    else: return;

    if(category != ''): query += ' AND LOWER(category) LIKE LOWER(\'%' + category + '%\')'; #LOWER is for ASCII only

    rows = fetch_db(update, context, query);
    if(rows == None): return;
    elif (len(rows) == 0): update.message.reply_text(fr'В базе данных нет сведений'); return;
    else: print_db(update, context, rows);

    return;

def topup(reply_text, update: Update, context: CallbackContext, sign):

    words = reply_text.split();
    wlen = len(words);

    if(wlen < 2): help(update, context); return;
    if(wlen == 2): topup_db(sign, words[1], update, context);
    elif(wlen == 3): topup_db(sign, words[1], update, context, words[2]);
    elif(wlen >= 4): topup_db(sign, words[1], update, context, words[2], words[3]);

    return;

def rept(reply_text, update: Update, context: CallbackContext): #reports
    if(not checkuser(update, context)):
        return;

    words = reply_text.split(' ', 2);
    wlen = len(words);

    #текущий месяц, все категории
    if(wlen < 2): rept_db(update, context);
    #дата( один день или прмежуток), все категории
    elif(wlen == 2): rept_db(update, context, words[1]);
    #дата(один день или прмежуток) + категория
    elif(wlen >= 3): rept_db(update, context, words[1], words[2]);
    
    return;

def cmd(update: Update, context: CallbackContext) -> None:
    if(not checkuser(update, context)):
        return;
    if(update.message.text.startswith('+ ')):
        topup(update.message.text, update, context, 1);

    elif(update.message.text.startswith('- ')):
        topup(update.message.text, update, context, 0);

    elif(update.message.text.startswith('отчет') or update.message.text.startswith('? ')):
        rept(update.message.text, update, context);

    else: update.message.reply_text(fr'Неизвестная команда! Наберите /help для справки.');
    return;

def main() -> None:

    if(not create_db()): return;

    updater = Updater(TELE_KEY);
    dispatcher = updater.dispatcher;
    dispatcher.add_handler(CommandHandler('start', start));
    dispatcher.add_handler(CommandHandler('help', help));
    #dispatcher.add_handler(CommandHandler('rept', rept));
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, cmd));

    updater.start_polling();
    updater.idle();

if __name__ == '__main__':
    main()