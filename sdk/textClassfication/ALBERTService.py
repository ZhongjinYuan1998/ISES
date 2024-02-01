from sdk.textClassfication.ALBERTModel import ALBERTModel, data_generator
import numpy as np

class ALBERTService:
    import threading
    _instance_lock = threading.Lock()
    init_flag = False

    def __new__(cls, *args, **kwargs):
        if not hasattr(ALBERTService, "_instance"):
            with ALBERTService._instance_lock:
                if not hasattr(ALBERTService, "_instance"):
                    ALBERTService._instance = object.__new__(cls)
        return ALBERTService._instance

    # 保证bert只执行一次
    def __init__(self):
        if ALBERTService.init_flag:
            return
        self.model = ALBERTModel()
        ALBERTService.init_flag = True

    def get_relevant_sentence_by_albert(self, sentences):
        data = data_generator(sentences)
        y_pred = []
        for _ in data:
            y_pred = y_pred + self.model.model.predict(_).argmax(axis=1).tolist()

        position_sentences = np.asarray(sentences)[np.where(np.asarray(y_pred) == 1)]
        
        return position_sentences
