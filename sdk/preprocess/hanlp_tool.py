import hanlp

class GlobalVar:#全局变量类
	def __init__(self):
		self.global_dict={} # 初始化全局变量字典
	def set_value(self, key, value):
		self.global_dict[key]=value#将全局变量加入字典，即定义一个全局变量
	def get_value(self, key):
		try:
			return self.global_dict[key]#访问全局变量，不存在则提示读取对应变量失败
		except:
			return -1
                
globalData = GlobalVar()

class hanlp_tool:
    def __init__(self, sentences):
        self.sentences = sentences
        self.hanlp_origin = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)
        for sen in sentences:
            if globalData.get_value("[cut]"+sen) == - 1:
                globalData.set_value("[cut]"+sen,self.hanlp_origin(sen, tasks='tok/fine')["tok/fine"])
            if globalData.get_value("[pos]"+sen) == - 1:
                globalData.set_value("[pos]"+sen,self.hanlp_origin(sen, tasks='pos/ctb')["pos/ctb"])
            if globalData.get_value("[dep]"+sen) == - 1:
                globalData.set_value("[dep]"+sen,self.hanlp_origin(sen, tasks="dep")["dep"])

    def cut(self):
        # return self.hanlp_origin(self.sentences, tasks='tok/fine')["tok/fine"]
        temp = []
        for sen in self.sentences:
            temp.append(globalData.get_value("[cut]"+sen))
        return temp
    
    def posTag(self):
        # return self.hanlp_origin(self.sentences, tasks='pos/ctb')["pos/ctb"]
        temp = []
        for sen in self.sentences:
            temp.append(globalData.get_value("[pos]"+sen))
        return temp
    
    def dependencyParsing(self):
        # return self.hanlp_origin(self.sentences, tasks="dep")["dep"]
        temp = []
        for sen in self.sentences:
            temp.append(globalData.get_value("[dep]"+sen))
        return temp
    
    def getResult(self):
        return self.cut(),self.posTag(),self.dependencyParsing()