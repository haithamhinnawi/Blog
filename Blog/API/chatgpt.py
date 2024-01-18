from openai import OpenAI

from blogs.dataclasses import Settings

settings = Settings()
client = OpenAI(
    api_key= settings.secret_key
)
class ChatGPTClient:
   @staticmethod
   def connect(message):
      chat_completion = client.chat.completions.create(
         messages=[
            {
               'role': 'user',
               'content': message
            }
         ],
         model='gpt-3.5-turbo'
      )
      return chat_completion.choices[0].message.content
   