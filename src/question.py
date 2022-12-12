import json


class Question(object):

    def __init__(self, text, answer, answer_type):
        self.text = text
        self.answer = answer
        self.answer_type = answer_type


    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4, ensure_ascii=False)