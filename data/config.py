from environs import Env
import sys 
import os 

sys.path.append(os.getcwd())
# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

GROUP_ID = env.int("GROUP_ID")
BOT_TOKEN = env.str("BOT_TOKEN")  # токен 
my_channel_id = env.int("my_channel_id")

id_kedr_ru=env.int("id_kedr_ru")


