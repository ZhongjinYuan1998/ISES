from sdk.graph.graph import graph
from sdk.rules.rules import rules
from sdk.preprocess.hanlp_tool import hanlp_tool
from sdk.preprocess.get_action_owner import get_action_owner
from sdk.preprocess.bad_words import cc_words,preprocess_words_1
from sdk.textClassfication_shixu.ALBERTService import ALBERTService as ALBERTService_shixu
import copy

def relationExtraction(sentences:list,shixu:list=[],is_use=True):
    if is_use == False:
        shixu = [2 for _ in range(len(sentences))]

    albert_service_shixu = ALBERTService_shixu()
    sentences_with_shixu = [sentences[0]]
    for i in range(1,len(sentences)):
        t = albert_service_shixu.get_shixu_by_albert([sentences_with_shixu[-1] + sentences[i]])
        if t[0] == 0:
            temp = copy.copy(sentences_with_shixu[-1])
            sentences_with_shixu[-1] = sentences[i]
            sentences_with_shixu.append(temp)
        elif t[0] == 1:
            sentences_with_shixu[-1] += "，" + sentences[i]
        else:
            sentences_with_shixu.append(sentences[i])

    g = graph()

    '''
        初始化开始节点
    '''
    g.setStartNode()

    '''
        初始化特征词匹配，分词，词性分析，依存句法分析
    '''
    rule = rules()
    words = []
    pos = []
    for sen in sentences:
        # print(sen)
        Hanlp = hanlp_tool(sen)
        words.append(Hanlp.cut())
        pos.append(Hanlp.posTag())

    # print("words",words)
    # print("pos",pos)

    '''
        预处理并列句
        【备注】pos[index][0] == "CC"用于判断是否并列句
    '''
    for i in range(len(words)):
        words_tmp = []
        for index,word in enumerate(words[i]):
            if (pos[i][index][0] == "CC" or word[0] in preprocess_words_1)  and word[0] in cc_words and len(words_tmp) != 0:
                words_tmp[-1] = words_tmp[-1] + ["同时"] + word[1:]
            else:
                words_tmp.append(word)
        words[i] = words_tmp

    # print("words",words)

    '''
        处理每一个分句
    '''
    for i,word in enumerate(words):
        activities = []
        for w in word:
            # print("分句：",w)
            activities = activities + get_action_owner(rule,w,shixu[i],is_use)
        print(activities)
        g.addActivities(activities)

    '''
        设置结束节点
    '''
    g.setEndNode()
    return g