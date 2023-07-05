class Word:
    def __init__(self, dict):
        self.start = dict["start"]
        self.end = dict["end"]
        self.word = dict["word"]
        self.conf = dict["conf"]
    def to_string(self):
        return "{:20} from {:.2f} sec to {:.2f} sec, confidence is {:.2f}%".format(self.word, self.start, self.end, self.conf*100)