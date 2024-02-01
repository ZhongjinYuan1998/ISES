from bert4keras.tokenizers import Tokenizer
from bert4keras.backend import keras
from bert4keras.models import build_transformer_model
from bert4keras.snippets import DataGenerator, sequence_padding
from bert4keras.optimizers import Adam, extend_with_piecewise_linear_lr
from keras.layers import Lambda, Dense
import os

# 配置
class Config:
    def __init__(self):
        # 预训练模型名称
        self.model_name = "albert"
        # 类别列表
        self.class_list = [0,1]
        # 类别数
        self.num_classes = len(self.class_list)
        # epoch数
        self.epochs = 20
        # mini-batch
        self.batch_size = 16
        # 每句话处理长度（短填切长）
        self.pad_size = 64
        # 学习率
        self.learning_rate = 1e-5

        self.config_path = os.path.dirname(__file__) + "/albert/config.json"
        self.checkpoint_path = os.path.dirname(__file__) + "/albert/model.ckpt-100000"
        self.dict_path = os.path.dirname(__file__) + "/albert/vocab.txt"
        # 文本处理
        self.tokenizer = Tokenizer(self.dict_path)

class ALBERTModel(object):
    def __init__(self):
        config = Config()
        bert = build_transformer_model(config.config_path, config.checkpoint_path, model='albert', return_keras_model=False)
        num_classes = config.num_classes
        # 加载预训练模型
        output = Lambda(lambda x: x[:, 0], name='CLS-token')(bert.model.output)
        output = Dense(
            units=num_classes,
            activation='softmax',
            kernel_initializer=bert.initializer
        )(output)
        self.model = keras.models.Model(bert.model.input, output)
        # 派生为带分段线性学习率的优化器。
        # 其中name参数可选，但最好填入，以区分不同的派生优化器。
        AdamLR = extend_with_piecewise_linear_lr(Adam, name='AdamLR')
        self.model.compile(
            loss='sparse_categorical_crossentropy',
            optimizer=AdamLR(lr=config.learning_rate),
            metrics=['accuracy'],
        )
        self.model.load_weights(os.path.dirname(__file__) + '/best_model.weights')


class data_generator(DataGenerator):
    def __init__(self, data, batch_size=32, buffer_size=None):
        super().__init__(data, batch_size, buffer_size)
        self.config = Config()
    def __iter__(self, random=False):
        batch_token_ids, batch_segment_ids = [], []
        for is_end, (text) in self.sample(random):
            token_ids, segment_ids = self.config.tokenizer.encode(text, maxlen=self.config.pad_size)
            batch_token_ids.append(token_ids)
            batch_segment_ids.append(segment_ids)
            if len(batch_token_ids) == self.config.batch_size or is_end:
                batch_token_ids = sequence_padding(batch_token_ids)
                batch_segment_ids = sequence_padding(batch_segment_ids)
                yield [batch_token_ids, batch_segment_ids]
                batch_token_ids, batch_segment_ids = [], []
