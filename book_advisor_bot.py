import random
import sqlite3

conn = sqlite3.connect("books.db", check_same_thread=False)
cursor = conn.cursor()

import telebot
bot = telebot.TeleBot("1279074156:AAE7nxtjg2-OfAEeuWagWTeSW5phfPZMYxw")

def getList():
    results = []
    
    row = cursor.fetchone()
    while row:
        results.append(row[0])
        row = cursor.fetchone()
        
    return results

def getOptions(option):
    cursor.execute("SELECT name FROM " + option)

    return getList()

def getSections(category):
    cursor.execute("""
                   SELECT s.name 
                   FROM category c, section s
                   WHERE s.fkey_category = c.id
                   AND c.name = '""" + category + "'")
    
    return getList()

def getAuthors():
    cursor.execute("SELECT DISTINCT author FROM book")
    
    return getList()

def getBookList():
    bookList = []
    
    row = cursor.fetchone()
    
    while row:
        book = []
    
        for i in range(0, len(row)):
            book.append(row[i])
        
        bookList.append(book)    
        row = cursor.fetchone()
        
    return bookList
    

def getBooksBySection(section):
    cursor.execute("""
                   SELECT b.title, b.author, b.year, b.description, c.name, s.name
                   FROM book b, category c, section s
                   WHERE b.fkey_section = s.id
                   AND s.fkey_category = c.id
                   AND s.name = '""" + section + "'")
    
    return getBookList()

def getBooksByAuthor(author):
    cursor.execute("""
                   SELECT b.title, b.author, b.year, b.description, c.name, s.name
                   FROM book b, category c, section s, class cl
                   WHERE b.fkey_section = s.id
                   AND s.fkey_category = c.id
                   AND b.fkey_class = cl.id
                   AND b.author = '""" + author + "'")
        
    return getBookList()

def getBooksByClass(bookClass):
    cursor.execute("""
                   SELECT b.title, b.author, b.year, b.description, c.name, s.name
                   FROM book b, category c, section s, class cl
                   WHERE b.fkey_section = s.id
                   AND s.fkey_category = c.id
                   AND b.fkey_class = cl.id
                   AND cl.name = '""" + bookClass + "'")
    
    return getBookList()

def getBookTitles(bookList):
    bookTitles = []
    
    for book in bookList:
        title = book[0]
        
        if len(book[0]) > 30:
            title = book[0][0:30] + ' ...'
            
        bookTitles.append(title)
        
    return bookTitles

def test_send_message_with_markdown(self):
    markdown = """
    *bold text*
    _italic text_
    """
    msg = tb.send_message(chat_id, markdown, parse_mode="Markdown")
    assert msg.message_id

def printBook(book):
    title = '*Название*:  ' + book[0]
    author = '\n*Автор*:  ' + book[1]
    year = '\n*Год написания*:  ' + book[2]
    description = '\n\n*Описание:*  ' + book[3]
    category = '\n\n*Категория:*  ' + book[4]
    section = '\n*Жанр/Раздел:*  ' + book[5]
    
    inf = title + author + year + description + category + section
    return inf

def generateMarkup(valuesList):
    markup = telebot.types.InlineKeyboardMarkup()

    for value in valuesList:
        markup.add(telebot.types.InlineKeyboardButton(text=value, callback_data=value))
    
    return markup

def getBooks(call, text):
    global bookList, bookTitles
    
    if len(bookList) == 0:
        bot.send_message(call.message.chat.id, '\nИзвините, мы ничего не нашли по Вашему запросу.\nПопробуйте использовать другие параметры для поиска литературы.')
      
    else:
        if len(bookList) > 10:
            bookList = random.choices(bookList, k=10)
                
        bookTitles = getBookTitles(bookList)
        markupBooks = generateMarkup(bookTitles)
 
        bot.send_message(call.message.chat.id, text, parse_mode= "Markdown", reply_markup=markupBooks)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        

categoryList = getOptions('category')
sectionList = getOptions('section')
authorList = getAuthors()
classList = getOptions('class')
bookList = []
bookTitles = []

searhByAuthor = False

@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    markup = telebot.types.InlineKeyboardMarkup()
    
    markup.add(telebot.types.InlineKeyboardButton(text='Поиск по категории и жанру', callback_data='searhByCategory'))
    markup.add(telebot.types.InlineKeyboardButton(text='Поиск по автору', callback_data='searhByAuthor'))
    markup.add(telebot.types.InlineKeyboardButton(text='Просмотреть популярные/новинки', callback_data='searhByClass'))
    
    bot.send_message(message.chat.id, 'Привет! Мы подберем для Вас книгу, которая обязательно Вам понравится:) \nНачнем с поиска!', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def main_query_handler(call):
    global bookList, bookTitles, searhByAuthor
    
    bot.answer_callback_query(callback_query_id=call.id)
   
    if call.data == 'searhByCategory':
        markupCategory = generateMarkup(categoryList)
        
        bot.send_message(call.message.chat.id, '\nВы выбрали поиск по категории.\nТеперь давайте выберем категорию:', reply_markup=markupCategory)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        
    elif call.data in categoryList:
        sectionsByCategory = getSections(call.data)
        
        markupSection = generateMarkup(sectionsByCategory)
        
        bot.send_message(call.message.chat.id, '\nВы выбрали категорию: _' + call.data + '_.\nОсталось только выбрать жанр/раздел литературы:', parse_mode= "Markdown", reply_markup=markupSection)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    
    elif call.data in sectionList:
        bookList = getBooksBySection(call.data)
        text = '\nВот несколько книг по Вашему запросу.\nВыберите какую-либо книгу из списка ниже, чтобы увидеть полную информацию:'
        
        getBooks(call, text)
        
    elif call.data in bookTitles:
        for book in bookList:
            if (call.data == book[0] or call.data).startswith(str):
                text = printBook(book)
                bot.send_message(call.message.chat.id, text, parse_mode= "Markdown")  
        
    elif call.data == 'searhByAuthor':
        searhByAuthor = True
        bot.send_message(call.message.chat.id, '\nВы выбрали поиск по автору.\nВведите имя автора и мы попробуем Вам что-то подыскать;)')
        
    elif call.data in authorList:
        bookList = getBooksByAuthor(call.data)
        text = '\nУ нас есть несколько произведений этого автора.\nВыберите какую-либо книгу из списка ниже, чтобы увидеть полную информацию:'
        
        getBooks(call, text)
        
    elif call.data == 'searhByClass':
        markupClass = generateMarkup(classList)
        
        bot.send_message(call.message.chat.id, '\nВы выбрали поиск по категории (популярные/новинки).\nТеперь выберите категорию:', reply_markup=markupClass)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        
    elif call.data in classList:
        bookList = getBooksByClass(call.data)
        text = '\nВот несколько книг из раздела _' + call.data + '_.\nВыберите какую-либо книгу из списка ниже, чтобы увидеть полную информацию:'
        
        getBooks(call, text)
            

@bot.message_handler(func=lambda message: True)
def search(message):
    global bookList, bookTitles, searhByAuthor
    
    if searhByAuthor == True:
        inp = (message.text).title()
    
        if inp in authorList:
            bookList = getBooksByAuthor(inp)
            
            if len(bookList) > 10:
                bookList = random.choices(bookList, k=10)
                
            bookTitles = getBookTitles(bookList)
            markupBooks = generateMarkup(bookTitles)
            
            text = '\nКруто! У нас есть несколько произведений этого автора.\nВыберите какую-либо книгу из списка ниже, чтобы увидеть полную информацию:'
        
            bot.send_message(message.chat.id, text, reply_markup=markupBooks)
            
            searhByAuthor = False
        
        else:
            l  = inp.split(' ')
            valueList = [value for value in l if value]
            
            authors = []
            temp = authorList.copy()
        
            for value in valueList:
                for author in temp:
                    if value in author:
                        authors.append(author)
                        temp.remove(author)
                        
            if authors:
                markupAuthors = generateMarkup(authors)
        
                bot.send_message(message.chat.id, 'Вот что нам удалось найти по вашему запросу.\nВыберите какого-либо автора из списка ниже, чтобы увидеть список его книг:', reply_markup=markupAuthors)
                
                searhByAuthor = False
             
            else:   
                bot.reply_to(message,'Не круто(: \nК сожалению по вашему запросу ничего не удалось найти, попробуйте еще раз.')
                
    else:
        pass

bot.polling()
