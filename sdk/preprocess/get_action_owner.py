from sdk.preprocess.bad_words import not_verb_and_noun_words,condition_no_words,owner_list,no_owner_words,preprocess_words
from sdk.preprocess.hanlp_tool import hanlp_tool

def get_action_owner(rule,words):
    activities = []
    sentences, bat_words, order, type = rule.getRules(words)
    if type == "none":
        for index,sentence in enumerate(sentences):
            words = bat_words[index]
            if words[0] in condition_no_words:
                sentence = sentence[len(words[0]):]
                owner = get_owner(sentence)
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
                    activity = {
                        "id":-1,
                        "partition":"",
                        "label":"sentence",
                        "type":"condition_no",
                        "child":[]
                    }
                    activities.append(activity)
            else:
                owner = get_owner(sentence)
                action = get_action(sentence)
                print(owner,action)

                if action is not None:
                    activity = {
                        "id":-1,
                        "partition":owner,
                        "label":action,
                        "type":"action",
                        "child":[]
                    }
                    activities.append(activity)
                else:
                    activity = {
                        "id":-1,
                        "partition":"",
                        "label":sentence,
                        "type":"action",
                        "child":[]
                    }
                    activities.append(activity)

    elif type == "condition":
        words = bat_words[0]
        sentence = sentences[0]
        owner = get_owner(sentence)
        action = get_action(sentence)
        if action is not None:
            activity = {
                "id":-1,
                "partition":owner,
                "label":sentence,
                "type":"condition",
                "child":[]
            }
            activities.append(activity)
        else:
            activity = {
                "id":-1,
                "partition":"",
                "label":sentence,
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
                    activity = {
                        "id":-1,
                        "partition":"",
                        "label":sentence,
                        "type":"condition_no",
                        "child":[]
                    }
                    activities.append(activity)
            else:
                owner = get_owner(sentence)
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
                else:
                    activity = {
                        "id":-1,
                        "partition":"",
                        "label":sentence,
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

def get_action(sentence:str):
    action = None
    verb_pos = ["VC","VE","VV","P","BA"]
    ad_pos = ["AD"]
    cur_pos = 0
    Hanlp = hanlp_tool([sentence])
    words, pos, dep = Hanlp.getResult()
    words, pos, dep = words[0], pos[0], dep[0]
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

    return action

def get_owner(sentence:str):
    noun_pos = ["NN","NR"]
    verb_pos = ["VC","VE","VV","P","BA"]
    Hanlp = hanlp_tool([sentence])
    words, pos, dep = Hanlp.getResult()
    words, pos, dep = words[0], pos[0], dep[0]
    owner = ""
    for index,word in enumerate(words):
        if dep[index][1] == "nsubj" and pos[index] in noun_pos and word not in no_owner_words:
            owner = word
            for _ in reversed(range(index)):
                if pos[_] in noun_pos:
                    owner = words[_] + owner
                else:
                    break
            for _ in range(index+1,len(words)):
                if pos[_] in noun_pos:
                    owner = owner + words[_]
                else:
                    break
            return owner
        # elif owner in owner_list:
        #     return owner
        elif pos[index] in verb_pos:
            break
    return ""