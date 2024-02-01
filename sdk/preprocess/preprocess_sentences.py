from sdk.preprocess.hanlp_tool import hanlp_tool
from sdk.preprocess.bad_words import bad_words,preprocess_words,preprocess_words_1

def filter_sentences(sentences:list):
    sentences = filter_sentences_by_preprocess_words(sentences)
    print("1",sentences)
    sentences = split_sentence_by_mark(sentences)
    print("2",sentences)
    sentences = filter_sentences_by_bad_words(sentences)
    print("3",sentences)
    # Hanlp = hanlp_tool(sentences)
    # print(Hanlp.getResult())
    # pos = Hanlp.posTag()
    # sentences = filter_sentences_by_verb_words(sentences, pos)
    # print("4",sentences)
    return sentences

def split_sentence_by_mark(sentences:list):
    mark = ["，", "。", "\n", "\r\n", ";", "；",","]
    for _ in mark:
        sentences = [s.split(_) for s in sentences]
        sentences = [_ for s in sentences for _ in s]

    return sentences

def filter_sentences_by_bad_words(sentences:list):
    return [_ for _ in sentences if _ not in bad_words]

def filter_sentences_by_verb_words(sentences,pos):
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
    return results

def filter_sentences_by_preprocess_words(sentences):
        for index,sentence in enumerate(sentences):
            for c in preprocess_words:
                sentences[index] = sentences[index].replace(c+"，",c).replace(c+".",c).replace(c+",",c).replace(c+"。",c).replace(c+";",c).replace(c+"；",c)

        for index,sentence in enumerate(sentences):
            for c in preprocess_words_1:
                sentences[index] = sentences[index].replace("，"+c,c).replace("."+c,c).replace(","+c,c).replace("。"+c,c).replace(";"+c,c).replace("；"+c,c)

        return sentences
