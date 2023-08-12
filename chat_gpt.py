import json
import sqlite3
import openai
import tiktoken
import skyeng_openai_functions
from typing import Dict, Any
from datetime import datetime
from skyeng_database import SkyengDatabase
from skyeng_user import SkyengUser

Message = Dict[str, Any]


class ChatGPT:
    def __init__(self, config):
        openai.api_key = config['openai_api_key']
        self.config = config
        self.model = config["gpt_model"]
        self.conn = sqlite3.connect(config["context_db_filename"], check_same_thread=False)
        self.create_table()
        self.encoding_model_messages = config["encoding_model_messages"]
        self.encoding_model_strings = config["encoding_model_strings"]
        self.llm_max_tokens = config["llm_max_tokens"]
        self.skyeng_db = SkyengDatabase(config)

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, chat_id INTEGER, role TEXT, content TEXT, function_name TEXT, arguments TEXT, timestamp TIMESTAMP)''')
        self.conn.commit()

    def get_messages(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT role, content FROM messages WHERE chat_id = ? ORDER BY timestamp ASC", (chat_id,))
        messages = []
        num_tokens = 0

        prompt_message = {"role": "system", "content": self.config["prompt"]}

        messages.append(prompt_message)
        num_tokens += self.num_tokens_from_message(prompt_message)

        for row in cursor.fetchall():
            role, content = row
            message = {"role": role, "content": content}
            num_tokens += self.num_tokens_from_message(message)
            if num_tokens > self.llm_max_tokens:
                break
            messages.append(message)

        return messages

    def num_tokens_from_message(self, message):
        try:
            encoding = tiktoken.encoding_for_model(self.encoding_model_messages)
        except KeyError:
            encoding = tiktoken.get_encoding(self.encoding_model_strings)

        num_tokens = 4
        for key, value in message.items():
            num_tokens += len(encoding.encode(str(value)))
            if key == "name":
                num_tokens += -1
        return num_tokens

    def send_message(self, chat_id, role, content, function_name=None, arguments=None):
        cursor = self.conn.cursor()
        timestamp = datetime.now()
        cursor.execute(
            "INSERT INTO messages (chat_id, role, content, function_name, arguments, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (chat_id, role, content, function_name, json.dumps(arguments) if arguments else None, timestamp))
        self.conn.commit()

    def handle_function_call(self, user_id, function_name, arguments):
        skyeng_user = SkyengUser(user_id, self.skyeng_db)
        function_mapping = {
            "login": skyeng_user.login,
            "get_word_sets": skyeng_user.get_word_sets,
            "get_words_from_set": skyeng_user.get_words_from_set,
            "get_words_data": skyeng_user.get_words_data
        }

        return function_mapping.get(function_name, lambda *args: {"status": "error", "message": "Unknown function"})(**arguments)

    def process_completion(self, chat_id, messages, function_call):
        function_call_limit = 4
        call_count = 0

        while True:
            completion = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                functions=skyeng_openai_functions.all_functions,
                function_call=function_call
            )
            response = completion.choices[0].message
            messages.append(response)

            if response.get("function_call"):
                function_name = response["function_call"]["name"]
                args_text = response["function_call"]["arguments"]
                args = json.loads(args_text)
                result = self.handle_function_call(chat_id, function_name, args)
                function_response: Message = {"role": "function", "name": function_name, "content": json.dumps(result)}
                messages.append(function_response)

                call_count += 1
                if call_count >= function_call_limit:
                    function_call = "none"

                self.send_message(chat_id, "assistant", function_response["content"], function_name, args_text)
            else:
                break

        response_content = messages[-1]["content"]
        self.send_message(chat_id, "assistant", response_content)
        return response_content

    def receive_message(self, chat_id, content):
        self.send_message(chat_id, "user", content)
        messages = self.get_messages(chat_id)
        return self.process_completion(chat_id, messages, function_call="auto")

    def clear_messages(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        self.conn.commit()
