import os
import telebot
import openai
from dotenv import load_dotenv
from datetime import datetime
from src.llm.working_llm import AsqLlm
from src.data import working_db as db

# Config
load_dotenv()
TG_API_TOKEN = os.getenv('TELEGRAM_API_KEY')
LLM_API_KEY = os.getenv('ANTHROPIC_API_KEY')
LLM_MODEL = 'claude-3-haiku-20240307'
LLM_TEMPERATURE = 0.5
INPUT_TOKEN_LIMIT = 60000

bot = telebot.TeleBot(TG_API_TOKEN)

# def get_new_style():
#     style = 'Эпоха 17 века была ознаменована изысканностью и утонченностью языка. Тексты того времени часто отличались сложными синтаксическими конструкциями, использованием архаизмов и цветистыми метафорами. Особое внимание уделялось формальным обращениям и изысканным выражениям вежливости. Стиль написания был помпезным и возвышенным, что подчеркивало достоинство и благородство авторов и их персонажей.'
#     text = 'Осталось всего 10 дней до окончания действия самой массовой госпрограммы ипотечного кредитования — т.н. льготная ипотека с фиксированной ставкой в 8%. И это проблема, потому что без льгот ипотека, а за ней и рынок новостроек, может полностью встать. И банки, и чиновники уже ищут, чем поддержать балансирующий над пропастью рынок емкостью в несколько триллионов рублей. «При необходимости ведомство перезапустит субсидирование проектного финансирования строительства жилья», — заявил на этой неделе замминистра строительства и ЖКХ РФ Никита Стасишин на пленарной сессии форума недвижимости «Движение». То есть, еще не успев отменить льготную ипотеку, власти готовят пути отхода. В рукаве — еще один сильный козырь — семейная ипотека. Вроде бы, в нынешнем виде она тоже заканчивается с 1 июля, но есть нюанс. В ряде регионов она сохранится, плюс, остается опция для семей с детьми до шести лет и многое другое. При этом сам Владимир Путин недавно пообещал сохранить элементы семейной ипотеки как минимум до 2030 года. «Ставка в 6% по семейной ипотеке будет во всех городах, если у вас есть ребенок младше шести лет. Если у вас есть ребенок старше шести лет, то такой будет ставка в малых городах и для индивидуального жилищного строительства. Однако если вы берете рыночную ипотеку и у вас рождается ребенок, вы можете рефинансировать ставку до 6%», — приоткрыл Никита Стасишин ход переговоров строительного лобби с финансовым блоком.'
#     response = AsqLlm(model=LLM_MODEL, api_key=LLM_API_KEY, style=style, text=text, temperature=0.5).asq()


# user status
user_data = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Привет! Отправь мне стиль текста.')
    user_data[message.from_user.id] = {'step': 'style'}


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        bot.reply_to(message, 'Отправь команду /start для начала.')
        return

    if user_data[user_id]['step'] == 'style':
        user_data[user_id]['style'] = message.text
        user_data[user_id]['step'] = 'text'
        bot.reply_to(message, 'Отправь мне текст, который нужно переписать в указанном стиле.')
    elif user_data[user_id]['step'] == 'text':
        style = user_data[user_id]['style']
        text = message.text

        # Checking the length of tokens
        total_tokens = (len(style.split()) + len(text.split())) / 3.5
        if total_tokens > INPUT_TOKEN_LIMIT:
            bot.reply_to(message,
                         f'Суммарная длина сообщений превышает установленный лимит токенов в {INPUT_TOKEN_LIMIT}.')
            return

        # Sending a request to llm
        response = AsqLlm(model=LLM_MODEL, api_key=LLM_API_KEY, style=style, text=text, temperature=0.5).asq()
        answer = response.content[0].text

        db.save_to_db(table_name='requests',
                      user_id=user_id,
                      created=datetime.now(),
                      style=style,
                      text=text,
                      model=str(response.model),
                      input_tokens=int(response.usage.input_tokens),
                      output_tokens=int(response.usage.output_tokens),
                      response=str(response),
                      response_content=str(answer)
                      )

        # Sending a response to the user
        bot.reply_to(message, f'{answer}')
        user_data.pop(user_id)


if __name__ == '__main__':
    bot.polling()
