import os
import json
import re

class rules:
    def __init__(self):
        self.data = {"preOrder":{},"postOrder":{},"syncOrder":{}}
        self.rules_file = "rules.json"
        self.setData()

    def setData(self):
        with open(os.path.join(os.path.dirname(__file__),self.rules_file), encoding="utf-8") as fp:
            rules_data = json.loads(fp.read())

        self.data["preOrder"] = {"single":[],"both":[]}
        self.data["postOrder"] = {"single":[],"both":[]}
        self.data["syncOrder"] = {"single":[],"both":[]}

        orders = ["preOrder","postOrder","syncOrder"]
        labels = ["none","condition","forked"]
        for order in orders:
            json_data = rules_data[order]
            for data in json_data:
                if data["type"] == "single":
                    for label in labels:
                        if label in data.keys():
                            for _ in data[label]:
                                self.data[order]["single"].append(([_],label))
                elif data["type"] == "both":
                    for label in labels:
                        if label in data.keys():
                            for f in data[label][0]:
                                for s in data[label][1]:
                                    self.data[order]["both"].append(([f,s],label))
                else:
                    for label in labels:
                        if label in data.keys():
                            for _ in data[label]:
                                self.data[order]["both"].append((_,label))
        
    def getPreOrder(self):
        return self.data["preOrder"]
    
    def getPostOrder(self):
        return self.data["postOrder"]
    
    def getInOrder(self):
        return self.data["syncOrder"]
    
    def getRules(self, words):
        orders = ["preOrder","postOrder","syncOrder"]
        types = ["both","single"]
        words = "#".join(words)
        results = []

        for order in orders:
            for type in types:
                for c in self.data[order][type]:
                    pattern = '(.*)'
                    for _ in c[0]:
                        pattern += _ + '(.*)'
                    ans = re.findall(pattern, words)
                    if len(ans) != 0:
                        ans = list(ans[0])
                        ans_1 = [_.split("#") for _ in ans if _ != ""]
                        ans_2 = ["".join(_.split("#")) for _ in ans if _ != ""]
                        results.append((ans_2, ans_1, order, c[1]))
        
        for _ in results:
            if _[2] != "none":
                return _
            
        if len(results) != 0:
            return results[0]
        else:
            return ["".join(words.split("#"))],[words.split("#")],"next","none"