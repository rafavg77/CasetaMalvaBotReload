import os
import logging
from socket import MsgFlag
from urllib import response
from telebot import types, telebot
from configparser import ConfigParser
import ipinfo
import json
import requests
import subprocess

# Cargar archivo de configuración
thisfolder = os.path.dirname(os.path.abspath(__file__))
initfile = os.path.join(thisfolder, 'utils/config/config.ini')
config = ConfigParser()
config.read(initfile)

# Configuracion de loggeo
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar parametros
BOT_TOKEN = config.get('params','telegram_token')
BOT_CHAT = config.get('params','telegram_chat_id')
BOT_GROUP = config.get('params','telegram_group_id')
USARUIOS_PERMITIDOS = config.get('base','permited')
TOKEN_INFO = config.get('base','token_info')
URL_NGROK = config.get('base','ulr_ngrok')

# Configuración de Constantes
statusVPN = '💳 Consultar estatus de VPN 💳'
vpnUP = '💡 Levantar VPN 💡'
vpnDONW = '🚿 Bajar VPN 🚿'
getPublicIP = '🔥 Consultar IP pública de la caseta 🔥'
ping = '🏓 Hacer un ping al bot 🏓'

# Inicializar funcionamiento del Bot
bot = telebot.TeleBot(BOT_TOKEN)

def esPermitido(message):
    if str(message.chat.id) in USARUIOS_PERMITIDOS:
        permitido = True
    else:
        permitido = False
        id = str(message.chat.id)
        if message.chat.type == 'group':
            user = str(message.chat.title)
        else:
            user = str(message.chat.username)
        logger.warning("Warning user without permission: " + id + " "+ user)
        bot.send_message(message.chat.id, "No tienes privilegios suficientes")
        bot.send_message(BOT_CHAT, "REPORTE usuario no permitido id: " + id + " nombre: "+ user)
    return permitido


# Condifuración del teclado
def keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=4)
    itembtna = types.KeyboardButton(statusVPN)
    itembtnv = types.KeyboardButton(vpnUP)
    itembtnc = types.KeyboardButton(vpnDONW)
    itembtnd = types.KeyboardButton(getPublicIP)
    itembtne = types.KeyboardButton(ping)
    markup.row(itembtna)
    markup.row(itembtnv)
    markup.row(itembtnc)
    markup.row(itembtnd)
    markup.row(itembtne)
    return markup

# Leer comandos de '/start' y '/help y crear teclado' 
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if esPermitido(message):
        bot.send_message(message.chat.id, "Puedes utilizar el teclado",reply_markup=keyboard())

# Comando ejecutar consulta al servicio Ngrok
def getNgrokStatus():
    logger.info('Consultando Servicio de VPN... ')
    r = requests.get('{}'.format(URL_NGROK), json={"key": "value"},timeout=10)
    if r.status_code == 200:
        response = r.json()
        botAnswer = response['tunnels'][0]['public_url']
        logger.info(botAnswer)
    elif r.status_code == 404:
        logger.error('Not Found.')
        botAnswer = "No se puede consultar el estatus del puerto"
    return botAnswer

# Comando para consultar estatus de VPN 
@bot.message_handler(commands=['getVpnStatus'])
def getVpnStatus(message):
    if esPermitido(message):
        #bot.send_message(message.chat.id, "Consultando VPN Status")
        try:
            botAnswer = getNgrokStatus()
            bot.send_message(message.chat.id,botAnswer)
        except Exception as e:
            bot.send_message(message.chat.id,e)
            pass
        

#Comando para levantar VPN
@bot.message_handler(commands=['setVpnUp'])
def setVpnUp(message):
    if esPermitido(message):
        bot.send_message(message.chat.id, "Levantando VPN")

        #Ejecuta comando para levantar servicio de VPN
        logger.info('He recibido un comando UP')
        p = subprocess.Popen("sudo service ngrok start", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        logger.info("Command output : ", output)

        botAnswer = getNgrokStatus()
        bot.send_message(message.chat.id,botAnswer)

#Comando para bajar VPN
@bot.message_handler(commands=['setVpnDown'])
def setVpnDown(message):
    if esPermitido(message):
        bot.send_message(message.chat.id, "Bajando VPN")

        #Ejecuta comando para bajar el servicio de VPN
        logger.info('He recibido un comando UP')
        p = subprocess.Popen("sudo service ngrok stop", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        logger.info("Command output : ", output)
        bot.send_message(message.chat.id,"Se bajó el servicio de VPN")

#Comando para consultar IP Publica
@bot.message_handler(commands=['getPublicIPInfo'])
def getPublicIPInfo(message):
    if esPermitido(message):
        handler = ipinfo.getHandler(TOKEN_INFO)
        details = handler.getDetails()
        bot.send_message(message.chat.id, "La IP Pública de la caseta es: " + details.ip)

#Comando que recibe ping y reponde pong
@bot.message_handler(commands=['makePing'])
def makePing(message):
    if esPermitido(message):
        bot.send_message(message.chat.id, "Pong 🏓")


# Funcion para detectar entradas de teclado de telegram
@bot.message_handler(func=lambda message:True)
def all_messages(message):
    if esPermitido(message):
        if message.text == statusVPN:
            getVpnStatus(message)
        elif message.text ==  vpnUP:
            setVpnUp(message)
        elif message.text == vpnDONW:
            setVpnDown(message)
        elif message.text == getPublicIP:
            getPublicIPInfo(message)
        elif message.text == ping:
            makePing(message)


# Ejecución Inicial del Bot
logger.info("🐧Bot is Running 🐧")
bot.send_message(BOT_GROUP, "🐧Bot is Running 🐧")
# Consultando IP Pública de la Caseta
handler = ipinfo.getHandler(TOKEN_INFO)
details = handler.getDetails()
bot.send_message(BOT_GROUP, "La IP Pública de la caseta es: " + details.ip)
bot.infinity_polling()