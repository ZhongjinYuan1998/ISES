from sdk.preprocess.bad_words import not_verb_and_noun_words,condition_no_words,owner_list,no_owner_words,preprocess_words
from sdk.preprocess.hanlp_tool import hanlp_tool

def get_action_owner(rule,words,shixu,is_use):
    activities = []
    sentences, bat_words, order, type = rule.getRules(words,shixu,is_use)
    # print(sentences,type)
    if type == "none":
        for index,sentence in enumerate(sentences):
            words = bat_words[index]
            if words[0] in condition_no_words:
                sentence = sentence[len(words[0]):]
                owner = get_owner(sentence)
                if owner == "我们":
                    owner = "用户"
                action = get_action(sentence)
                if action is not None:
                    activity = {
                        "id":-1,
                        "partition":owner,
                        "label":action,
                        "type":"condition_no",
                        "child":[]
                    }
                    activities.append(activity)
            else:
                owner = get_owner(sentence)
                if owner == "我们":
                    owner = "用户"
                action = get_action(sentence)

                if action is not None:
                    activity = {
                        "id":-1,
                        "partition":owner,
                        "label":action,
                        "type":"action",
                        "child":[]
                    }
                    activities.append(activity)

    elif type == "condition":
        words = bat_words[0]
        sentence = sentences[0]
        owner = get_owner(sentence)
        if owner == "我们":
            owner = "用户"
        action = get_action(sentence)
        if action is not None:
            activity = {
                "id":-1,
                "partition":owner,
                # "label":sentence,
                "label":action,
                "type":"condition",
                "child":[]
            }
            activities.append(activity)
        for index in range(1,len(sentences)):
            sentence = sentences[index]
            words = bat_words[index]
            if words[0] in condition_no_words:
                sentence = sentence[len(words[0]):]
                owner = get_owner(sentence)
                if owner == "我们":
                    owner = "用户"
                action = get_action(sentence)
                if action is not None:
                    activity = {
                        "id":-1,
                        "partition":owner,
                        "label":action,
                        "type":"condition_no",
                        "child":[]
                    }
                    activities.append(activity)
            else:
                owner = get_owner(sentence)
                if owner == "我们":
                    owner = "用户"
                action = get_action(sentence)
                if action is not None:
                    activity = {
                        "id":-1,
                        "partition":owner,
                        "label":action,
                        "type":"action",
                        "child":[]
                    }
                    activities.append(activity)

    elif type == "forked":
        _type = "forked"
        for index in range(len(sentences)):
            sentence = sentences[index]
            words = bat_words[index]
            if words[0] in condition_no_words:
                _type = "forked"
            owner = get_owner(sentence)
            if owner == "我们":
                owner = "用户"
            action = get_action(sentence)
            if action is None:
                action = sentence
            activity = {
                "id":-1,
                "partition":owner,
                "label":action,
                "type":_type,
                "child":[]
            }
            activities.append(activity)

    return activities

def get_action_owner_no(sentences):
    activities = []
    for index,sentence in enumerate(sentences):
        # print("s",sentence)
        owner = get_owner(sentence)
        action = get_action(sentence)
        if action is not None:
            type = "action"
            if "如果" in sentence:
                type = "condition"
            elif "否则" in sentence:
                type = "condition_no"
            activity = {
                "id":-1,
                "partition":owner,
                "label":action,
                "type":type,
                "child":[]
            }
            activities.append(activity)

    return activities

def get_action(sentence:str):
    action = None
    verb_pos = ["VC","VE","VV","P","BA"]
    ad_pos = ["AD"]
    cur_pos = 0
    Hanlp = hanlp_tool([sentence])
    words, pos, dep = Hanlp.getResult()
    words, pos, dep = words[0], pos[0], dep[0]
    # print(words, pos, dep)
    for index,word in enumerate(words):
        if pos[index] in verb_pos:
            break
        else:
            cur_pos += len(word)

    if cur_pos < len(sentence):
        action = sentence[cur_pos:]
        for _ in reversed(range(index)):
            if pos[_] in ad_pos and words[_] not in preprocess_words:
                action = words[_] + action
            else:
                break

    # print(action)
    return action

def get_owner(sentence:str):
    noun_pos = ["NN","NR","PN"]
    verb_pos = ["VC","VE","VV","P","BA"]
    Hanlp = hanlp_tool([sentence])
    words, pos, dep = Hanlp.getResult()
    words, pos, dep = words[0], pos[0], dep[0]
    # print(sentence, words, pos, dep)
    for index,word in enumerate(words):
        if pos[index] in verb_pos and not (index == 0 and pos[0]=="P"):
            break
        elif dep[index][1] == "nsubj" and pos[index] in noun_pos and word not in no_owner_words:
            for _ in reversed(range(index)):
                if pos[_] in noun_pos:
                    word = words[_] + word
                else:
                    break
            for _ in range(index+1,len(words)):
                if pos[_] in noun_pos:
                    word = word + words[_]
                else:
                    break
            return word
        elif word in owner_list:
            return word
    return ""