import yaml
import logging
import telebot
from config import YAML

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s|%(levelname)s|%(message)s", level=logging.INFO)


token = YAML["telegram"]["token"]
chats_admin_ids = YAML["telegram"]["chats_admin_ids"]

bot = telebot.TeleBot(token=token)
