import hanlp

class hanlp_tool:
    def __init__(self, sentences):
        self.sentences = sentences
        self.hanlp_origin = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)

    def cut(self):
        return self.hanlp_origin(self.sentences, tasks='tok/fine')["tok/fine"]
    
    def posTag(self):
        return self.hanlp_origin(self.sentences, tasks='pos/ctb')["pos/ctb"]
    
    def dependencyParsing(self):
        return self.hanlp_origin(self.sentences, tasks="dep")["dep"]
    
    def getResult(self):
        return self.cut(),self.posTag(),self.dependencyParsing()