import requests
import json
import html
import re
import random
import string

# logging
import logging
logger = logging.getLogger(__name__)


class TriviaDB:
    '''
    Class to communicate with the online, free DB
    '''    

    def __init__(self) -> None:
        self.base_http = f'https://opentdb.com/api.php?'

    def get(self, num_questions=None) -> dict:
        if num_questions is None:
            self.base_http = f'https://opentdb.com/api.php?amount=1'  # 1 q by default
        else:
            self.base_http = f'https://opentdb.com/api.php?amount={num_questions}'

        response = requests.get(self.base_http)
        #response_str = html.unescape(response.text)

        try:
            data = json.loads(response.text)
            return data.get('results')
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from response: {response.text}")
            return None

    def get_question(self):
        for result in self.get():
            return result
    

# db = TriviaDB()
# result = db.get_question()

# category = result['category']
# type = result['type']
# difficulty = result['difficulty']
# question = result['question']
# correct_ans = result['correct_answer']
# incorrect_ans = result['incorrect_answers']