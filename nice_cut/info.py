class Info:

    # Value such as '00:16:18,520'
    end_time: str
    # Value such as '00:16:20,850'
    start_time: str
    sentences: str
    # Value such as '00:16:18,520 --> 00:16:20,850'
    time_duration: str
    number: str
    srt_number: str
    # time_durations: list
    next_info: None

    def __init__(self, next_info):
        self.next_info = next_info
        pass

    def __init__(self, number, time_duration):
        self.number = str.strip(number)
        self.srt_number = str.strip(number)
        self.time_duration = str.strip(time_duration)
        self.sentences = ''
        # self.time_durations.append(str.strip(time_duration))

    def set_time(self, time_duration):
        self.start_time = str.split(str.strip(time_duration), ' --> ')[0]
        self.end_time = str.split(str.strip(time_duration), ' --> ')[1]

    def append_sentence(self, sentences):
        if str.strip(sentences) != '' and self.sentences != '':
            self.sentences = self.sentences + ' ' + str.strip(sentences)
        elif str.strip(sentences) != '':
            self.sentences = str.strip(sentences)

    def append_sentence_2_beginning(self, sentences):
        self.sentences = str.strip(sentences) + ' ' + str.strip(self.sentences)

    # def save_time_durations(self, td):
    #     self.time_durations.append(td)
