from sdk.graph.graph import graph
from sdk.rules.rules import rules
from sdk.preprocess.hanlp_tool import hanlp_tool
from sdk.preprocess.get_action_owner import get_action_owner
from sdk.preprocess.bad_words import cc_words,preprocess_words_1

def relationExtraction(sentences:list):
    g = graph()

    '''
        初始化开始节点
    '''
    g.setStartNode()

    '''
        初始化特征词匹配，分词，词性分析，依存句法分析
    '''
    rule = rules()
    Hanlp = hanlp_tool(sentences)
    words = Hanlp.cut()
    pos = Hanlp.posTag()

    '''
        预处理并列句
        【备注】pos[index][0] == "CC"用于判断是否并列句
    '''
    words_tmp = []
    for index,word in enumerate(words):
        if (pos[index][0] == "CC" or word[0] in preprocess_words_1)  and word[0] in cc_words and len(words_tmp) != 0:
                words_tmp[-1] = words_tmp[-1] + ["同时"] + word[1:]
        else:
            words_tmp.append(word)
    words = words_tmp

    '''
        处理每一个分句
    '''
    for word in words:
        print(word)
        activities = get_action_owner(rule,word)
        print(activities)
        g.addActivities(activities)

    '''
        设置结束节点
    '''
    g.setEndNode()
    return g