import os

import openai
from config import *

openai.api_key = DefaultData['apikey']
models = openai.Model.list()


print(models)