from sdk.preprocess.hanlp_tool import hanlp_tool
from sdk.preprocess.bad_words import bad_words,preprocess_words,preprocess_words_1

def filter_sentences(sentences:list):
    sentences = filter_sentences_by_preprocess_words(sentences)
    sentences = split_sentence_by_mark(sentences)
    sentences = filter_sentences_by_bad_words(sentences)
    for index,sen in enumerate(sentences):
        Hanlp = hanlp_tool(sentences[index])
        pos = Hanlp.posTag()
        # print(pos,sentences[index])
        sentences[index] = filter_sentences_by_verb_words(sentences[index], pos)
        # print(sentences)
    return sentences

def split_sentence_by_mark(sentences:list):
    mark = ["，", "。", "\n", "\r\n", ";", "；",","]
    sentences = [[s] for s in sentences]
    for index,sentence in enumerate(sentences):
        for _ in mark:
            sentences[index] = [s.split(_) for s in sentences[index]]
            sentences[index] = [s for sen in sentences[index] for s in sen if s != ""]

    return sentences

def filter_sentences_by_bad_words(sentences:list):
    for index,sen in enumerate(sentences):
        sentences[index] = [_ for _ in sentences[index] if _ not in bad_words]
    return sentences

def filter_sentences_by_verb_words(sentences,pos):
    # print("test",sentences,pos)
    verb_words = ["VV","VC","VE"]
    results = []
    for index,sentence in enumerate(sentences):
        is_action = False
        for _ in pos[index]:
            if _ in verb_words:
                is_action = True
                break
        if is_action:
            results.append(sentence)
    # print("s",results)
    return results

def filter_sentences_by_preprocess_words(sentences):
        for index,sentence in enumerate(sentences):
            for c in preprocess_words:
                sentences[index] = sentences[index].replace(c+"，",c).replace(c+".",c).replace(c+",",c).replace(c+"。",c).replace(c+";",c).replace(c+"；",c)

        for index,sentence in enumerate(sentences):
            for c in preprocess_words_1:
                sentences[index] = sentences[index].replace("，"+c,c).replace("."+c,c).replace(","+c,c).replace("。"+c,c).replace(";"+c,c).replace("；"+c,c)

        return sentences
