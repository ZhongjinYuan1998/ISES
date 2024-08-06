import json
from graphviz import Digraph
import difflib
from plantuml import PlantUML
import time
import os

class graph:
    def __init__(self):
        self.data = {"nodes":[],"edges":[]}
        '''
            活动图的分支，即树的叶子节点
        '''
        self.cur_nodes = []
        '''
            分叉-连接节点列表
        '''
        self.forked_nodes = []
        '''
            当前条件节点的描述
        '''
        self.condition_label = ""
        self.is_connect = 0
        self.condition_partition = ""

    def _print(self):
        print("------graph start------")
        print(json.dumps(self.data, indent=2, ensure_ascii=False))
        print("-------graph end-------")

    def _save(self,filename):
        with open(filename+".nodes","w",encoding="utf-8") as f:
            for node in self.data["nodes"]:
                f.write(node["label"])
                f.write("\n")

        with open(filename+".edges","w",encoding="utf-8") as f:
            for edge in self.data["edges"]:
                f.write(self.data["nodes"][edge["source"]]["label"] + "->" + self.data["nodes"][edge["target"]]["label"])
                f.write("\n")

    def _draw(self,filename="out",directory=".\\",null_show=True):
        if null_show==False and len(self.data["nodes"]) <= 2:
            return 

        dot = Digraph(name="p", comment="", format="png")
        for node in self.data["nodes"]:
            dot.node(str(node["id"]),node["partition"]+"-->"+node["label"],fontname="FangSong")
        for edge in self.data["edges"]:
            dot.edge(str(edge["source"]),str(edge["target"]),label=edge["label"],fontname="FangSong")
        dot.render(filename,directory)

    def get_edge_label(self,source,target):
        label = ""
        for e in self.data["edges"]:
            if e["source"] == source and e["target"] == target:
                label = e["label"]
                break
        return label
    
    def get_plantuml_str(self,node,flag=0,content=""):
        plantuml_str = []
        is_condition = 0
        if flag == 1:
            plantuml_str.append("|"+node["partition"]+"|\n"+"if ("+content+") then (是)")
            plantuml_str.append("|"+node["partition"]+"|\n:"+node["label"]+";")
        elif flag == -1:
            # print("node",node)
            plantuml_str.append("|"+node["partition"]+"|\n"+"elseif ("+content+") then (是)")
            plantuml_str.append("|"+node["partition"]+"|\n:"+node["label"]+";")
        elif flag == 2:
            plantuml_str.append("|"+node["partition"]+"|\n:"+node["label"]+";")
            return plantuml_str
        elif flag == 3:
            plantuml_str.append("|"+node["partition"]+"|\n:"+node["label"]+";")
        elif node["label"] == "连接":
            plantuml_str.append("end fork")
            if node["type"] == "condition":
                is_condition = 1
        elif node["type"] == "end":
            plantuml_str.append("|"+node["partition"]+"|\nstop")
        elif node["type"] == "condition":
            plantuml_str.append("|"+node["partition"]+"|\n:"+node["label"]+";")
            is_condition = 1
        elif node["type"] == "start":
            plantuml_str.append("|"+node["partition"]+"|\nstart")
        elif node["type"] == "action":
            plantuml_str.append("|"+node["partition"]+"|\n:"+node["label"]+";")
        elif node["type"] == "condition_no":
            plantuml_str.append("else (否)")
            plantuml_str.append("|"+node["partition"]+"|\n:"+node["label"]+";")
        elif node["type"] == "fork":
            plantuml_str.append("|"+self.data["nodes"][node["child"][0]]["partition"]+"|")
            plantuml_str.append("fork")
        elif node["type"] == "join":
            plantuml_str.append("end fork")

        for i,child_i in enumerate(node["child"]):
            if is_condition == 1:
                if i == 0:
                    _content = self.get_edge_label(node["id"],child_i)
                    # _content = "|"+node["partition"]+"|\n"+"elseif ("+content+") then (是)"
                    plantuml_str += self.get_plantuml_str(self.data["nodes"][child_i],1,_content)
                    # plantuml_str.append("endif")
                elif i < len(node["child"]) - 1:
                    _content = self.get_edge_label(node["id"],child_i)
                    plantuml_str += self.get_plantuml_str(self.data["nodes"][child_i],-1,_content)
                else:
                    if self.data["nodes"][child_i]["type"] == "condition_no":
                        plantuml_str += self.get_plantuml_str(self.data["nodes"][child_i])
                        plantuml_str.append("endif")
                    else:
                        _content = self.get_edge_label(node["id"],child_i)
                        plantuml_str += self.get_plantuml_str(self.data["nodes"][child_i],-1,_content)
                        plantuml_str.append("endif")
            elif node["type"] == "fork":
                if i < len(node["child"]) - 1:
                    plantuml_str += self.get_plantuml_str(self.data["nodes"][child_i],flag=2)
                    plantuml_str.append("fork again")
                else:
                    plantuml_str += self.get_plantuml_str(self.data["nodes"][child_i],flag=3)
            else:
                plantuml_str += self.get_plantuml_str(self.data["nodes"][child_i])

        return plantuml_str

    def to_plantuml(self):
        # self.node_flag = [0 for _ in range(len(self.data["nodes"]))]
        plantuml_str = self.get_plantuml_str(self.data["nodes"][0])

        for i in range(len(plantuml_str)):
            if "|\n:分叉;" in plantuml_str[i]:
                plantuml_str[i] = "|" + plantuml_str[i].split("|")[1] + "|\nfork"

        par = ""
        for i in reversed(range(len(plantuml_str))):
            if "|\nif " in plantuml_str[i]:
                par = "|" + plantuml_str[i].split("|")[1] + "|"
                break

        p_flag = 0
        p1_flag = 0
        p_i = 0
        p1_i = 0
        p2_i = 0 
        p_tmp = []
        p1_tmp = []
        for i in range(len(plantuml_str)):
            if "|\n:可以" in plantuml_str[i]:
                p_flag = 1
                p_i = i
            if p_flag == 1 and "|\n:也可以" in plantuml_str[i] and i - p_i < 4:
                p1_flag = 1
                p1_i = i
            if p_flag == 1 and p1_flag != 1:
                p_tmp.append(plantuml_str[i])
            if p1_flag == 1:
                p1_tmp.append(plantuml_str[i])
                p2_i = i
                if plantuml_str[i] in p_tmp:
                    break

        print("p_tmp",p_tmp)
        print("p1_tmp",p1_tmp)

        if p1_flag == 1:
            plantuml_str.insert(p_i,"|" + p_tmp[0].split("|")[1] + "|\nif () then")
            plantuml_str[p1_i] = "|" + p1_tmp[0].split("|")[1] + "|\nelse"
            plantuml_str.insert(p2_i+1,"|" + p1_tmp[0].split("|")[1] + "|\nendif")

        # print(self.data["nodes"])
        print(plantuml_str)
        temp = []
        flag = 0
        for _ in plantuml_str:
            if "|\n:endif" in _:
                _ = _.replace("endif","") + "\nendif"
                flag = 1
            if flag == 1 and _ == "endif":
                flag = 0
            else:
                temp.append(_)

        plantuml_str = temp

        k = -1
        for i in reversed(range(len(plantuml_str))):
            if plantuml_str[i] == "endif":
                k = i
            elif plantuml_str[i] == "else (否)":
                k = -1
                break
            elif plantuml_str[i].startswith("if "):
                break

        if k != -1:
            _p = ""
            for i in reversed(range(len(plantuml_str))):
                # if "|\nif " in plantuml_str[i] or "|\nelseif " in plantuml_str[i]:
                if plantuml_str[i].startswith("if ") or plantuml_str[i].startswith("elseif "):
                    _p = "||"
                if _p == "||" and plantuml_str[i].startswith("|"):
                    _p = "|" + plantuml_str[i].split("|")[1] + "|"
                    break

            # print(plantuml_str)
            plantuml_str.insert(k,par + "\nelse (否)")
            if _p == "||":
                plantuml_str.insert(k+1,"stop")
            else:
                plantuml_str.insert(k+1,_p+"\nstop")

        flag = 0
        for i in reversed(range(len(plantuml_str))):
            if "else" in plantuml_str[i] and not "elseif" in plantuml_str[i]:
                break
            elif "|\nif " in plantuml_str[i]:
                flag = 1
                break

        if flag == 0:
            return "@startuml\n" + "\n".join(plantuml_str)+"\n@enduml"
        else:
            return "@startuml\n" + "\n".join(plantuml_str)+"\nelse\nstop\n@enduml"
    
    def to_plantuml_img(self, img_path):
        # 创建PlantUML对象并设置服务器的URL
        plant = PlantUML(url="http://www.plantuml.com/plantuml/img/")
        print(self.data)

        # 定义PlantUML代码
        uml_code = self.to_plantuml()
        print(uml_code)

        # 保存PlantUML代码到文件
        filename = str(time.time())
        with open(filename + ".puml", "w") as file:
            file.write(uml_code)

        # 生成PlantUML代码的图像表示
        image_path = plant.processes_file(filename + ".puml")
        os.rename(filename+".png",img_path)
        os.remove(filename + ".puml")

    def compare_str(self,str1,str2):
        if str1 == "" or str2 == "":
            return 0
        return difflib.SequenceMatcher(None, str1, str2).quick_ratio()
    
    def getConditionEdgeLabel(self):
        for index in reversed(range(len(self.data["edges"]))):
            if self.data["edges"][index]["label"] != "":
                return self.data["edges"][index]["label"]
        return ""

    def setStartNode(self):
        assert(len(self.data["nodes"])==0 and len(self.data["edges"])==0)
        startNode = {
            "id":0,
            "partition":"",
            "label":"起始",
            "type":"start",
            "child":[]
        }
        self.data["nodes"].append(startNode)

    def setNodePartition(self,id,partition):
        self.data["nodes"][id]["partition"] = partition
    
    def setNodeChild(self,id,child):
        self.data["nodes"][id]["child"].append(child)
        if self.data["nodes"][child]["partition"] == "":
            self.data["nodes"][child]["partition"] = self.data["nodes"][id]["partition"]

    def setAllNodePartition_1(self,node):
        for child_i in node["child"]:
            if self.data["nodes"][child_i]["partition"] == "":
                self.data["nodes"][child_i]["partition"] == node["partition"]

    def setAllNodePartition(self):
        is_set = False
        for node in self.data["nodes"]:
            if node["partition"] != "":
                is_set = True

        if not is_set:
            for index,node in enumerate(self.data["nodes"]):
                self.data["nodes"][index]["partition"] = "默认泳道"
        else:
            # print(self.data["nodes"])
            # for index in range(1,len(self.data["nodes"])):
            #     if self.data["nodes"][index]["partition"] == "":
            #         self.data["nodes"][index]["partition"] = self.data["nodes"][index-1]["partition"]
            # for index in reversed(range(0,len(self.data["nodes"])-1)):
            #     if self.data["nodes"][index]["partition"] == "":
            #         self.data["nodes"][index]["partition"] = self.data["nodes"][index+1]["partition"]

            self.setAllNodePartition_1(self.data["nodes"][0])

            for index in range(1,len(self.data["nodes"])):
                if self.data["nodes"][index]["partition"] == "":
                    self.data["nodes"][index]["partition"] = self.data["nodes"][index-1]["partition"]
            for index in reversed(range(0,len(self.data["nodes"])-1)):
                if self.data["nodes"][index]["partition"] == "":
                    self.data["nodes"][index]["partition"] = self.data["nodes"][index+1]["partition"]

            # for index in reversed(range(0,len(self.data["nodes"])-1)):
            #     if self.data["nodes"][index]["type"] == "condition":
            #         self.data["nodes"][index]["partition"] = self.data["nodes"][index+1]["partition"]
    
    def setEndNode(self):
        assert(len(self.data["nodes"])>0)

        # print("forked_nodes",self.forked_nodes)
        if len(self.forked_nodes) != 0:
            # assert(len(self.forked_nodes)>=2)
            source_id = len(self.data["nodes"]) - 1
            startNode = {
                "id":len(self.data["nodes"]),
                "partition":"",
                "label":"分叉",
                "type":"fork",
                "child":[]
            }
            edge = {
                "id":len(self.data["edges"]),
                "source":source_id,
                "target":startNode["id"],
                "relation":"",
                "label":self.condition_label
            }
            self.condition_label = ""
            self.data["edges"].append(edge)
            self.data["nodes"].append(startNode)
            self.setNodeChild(source_id,startNode["id"])
            endNode = {
                "id":len(self.data["nodes"]) + len(self.forked_nodes),
                "partition":"",
                "label":"连接",
                "type":"join",
                "child":[]
            }
            for index,node in enumerate(self.forked_nodes):
                node["id"] = len(self.data["nodes"])
                self.data["nodes"].append(node)
                if index > 0 and node["partition"] == "":
                    node["partition"] = self.forked_nodes[index-1]["partition"]
                self.setNodeChild(startNode["id"],node["id"])
                edge1 = {
                    "id":len(self.data["edges"]),
                    "source":startNode["id"],
                    "target":node["id"],
                    "relation":"",
                    "label":self.condition_label
                }
                self.condition_label = ""
                self.data["edges"].append(edge1)
                edge2 = {
                    "id":len(self.data["edges"]),
                    "source":node["id"],
                    "target":endNode["id"],
                    "relation":"",
                    "label":self.condition_label
                }
                self.condition_label = ""
                self.data["edges"].append(edge2)
            self.data["nodes"].append(endNode)
            for node in self.forked_nodes:
                self.setNodeChild(node["id"],endNode["id"])
            self.forked_nodes = []

        nodes_len = len(self.data["nodes"])
        for i in range(nodes_len):
            if len(self.data["nodes"][i]["child"]) == 0 and self.data["nodes"][i]["type"] != "end" and not self.data["nodes"][i]["label"].startswith("nostop"): 
                id = len(self.data["nodes"])
                endNode = {
                    "id":id,
                    "partition":"",
                    "label":"结束",
                    "type":"end",
                    "child":[]
                }
                endEdge = {
                    "id":len(self.data["edges"]),
                    "source":self.data["nodes"][i]["id"],
                    "target":id,
                    "relation":"next",
                    "label":self.condition_label
                }
                self.condition_label = ""
                self.data["nodes"].append(endNode)
                self.data["edges"].append(endEdge)
                self.setNodePartition(id,self.data["nodes"][i]["partition"])
                self.setNodeChild(self.data["nodes"][i]["id"],id)
                self.setAllNodePartition()
            if self.data["nodes"][i]["label"].startswith("nostop"):
                self.data["nodes"][i]["label"] = self.data["nodes"][i]["label"][6:]

    def addNextNode(self,curNode,relation="next"):
        if curNode["type"] != "forked":
            if len(self.forked_nodes) != 0:
                # print(self.forked_nodes)
                assert(len(self.forked_nodes)>=2)
                lastNodeId = len(self.data["nodes"])-1
                startNode = {
                    "id":len(self.data["nodes"]),
                    "partition":"",
                    "label":"分叉",
                    "type":"fork",
                    "child":[]
                }
                edge = {
                    "id":len(self.data["edges"]),
                    "source":lastNodeId,
                    "target":startNode["id"],
                    "relation":"",
                    "label":self.condition_label
                }
                self.condition_label = ""
                self.data["edges"].append(edge)
                self.data["nodes"].append(startNode)
                self.setNodeChild(lastNodeId,startNode["id"])
                endNode = {
                    "id":len(self.data["nodes"]) + len(self.forked_nodes),
                    "partition":"",
                    "label":"连接",
                    "type":"join",
                    "child":[]
                }
                for node in self.forked_nodes:
                    node["id"] = len(self.data["nodes"])
                    self.data["nodes"].append(node)
                    if node["partition"] == "":
                        node["partition"] = self.forked_nodes[0]["partition"]
                    self.setNodeChild(startNode["id"],node["id"])
                    edge1 = {
                        "id":len(self.data["edges"]),
                        "source":startNode["id"],
                        "target":node["id"],
                        "relation":"",
                        "label":self.condition_label
                    }
                    self.condition_label = ""
                    self.data["edges"].append(edge1)
                    edge2 = {
                        "id":len(self.data["edges"]),
                        "source":node["id"],
                        "target":endNode["id"],
                        "relation":"",
                        "label":self.condition_label
                    }
                    self.condition_label = ""
                    self.data["edges"].append(edge2)
                self.data["nodes"].append(endNode)
                for node in self.forked_nodes:
                    self.setNodeChild(node["id"],endNode["id"])
                self.forked_nodes = []

        special_types = ["condition_no","merge","forked","condition"]
        if curNode["type"] not in special_types:
            if self.is_connect == 0:
                startNodeId = len(self.data["nodes"])-1
                if len(self.cur_nodes) != 0:
                    startNodeId = self.cur_nodes[0]
            else:
                startNodeId = self.getConditionNodeId()
                self.is_connect = 0
            if startNodeId == 0 and self.data["nodes"][0]["partition"] == "":
                self.data["nodes"][0]["partition"] = curNode["partition"]
            if curNode["partition"] == "":
                curNode["partition"] = self.condition_partition
                self.condition_partition = ""
            curNode["id"] = len(self.data["nodes"])
            self.data["nodes"].append(curNode)
            self.setNodeChild(startNodeId,curNode["id"])
            edge = {
                "id":len(self.data["edges"]),
                "source":startNodeId,
                "target":curNode["id"],
                "relation":relation,
                "label":self.condition_label
            }
            self.condition_label = ""
            self.data["edges"].append(edge)
        elif curNode["type"] == "condition":
            self.condition_label = curNode["label"]
            self.condition_partition = curNode["partition"]
            startNodeId = self.getConditionNodeId()
            if startNodeId == len(self.data["nodes"])-1:
                self.data["nodes"][-1]["type"] = "condition"
            else:
                if self.compare_str(curNode["label"],self.getConditionEdgeLabel()) >= 0.1:
                    self.is_connect = 1
        elif curNode["type"] == "condition_no":
            startNodeId = self.getConditionNodeId()
            if startNodeId == 0 and self.data["nodes"][0]["partition"] == "":
                self.data["nodes"][0]["partition"] = curNode["partition"]
            curNode["id"] = len(self.data["nodes"])
            self.data["nodes"].append(curNode)
            self.setNodeChild(startNodeId,curNode["id"])
            edge = {
                "id":len(self.data["edges"]),
                "source":startNodeId,
                "target":curNode["id"],
                "relation":relation,
                "label":self.condition_label
            }
            self.condition_label = ""
            self.data["edges"].append(edge)
            self.cur_nodes = [len(self.data["nodes"])-2,len(self.data["nodes"])-1]
        elif curNode["type"] == "merge":
            assert(len(self.data["nodes"])>1)
            curNode["id"] = len(self.data["nodes"])
            self.data["nodes"].append(curNode)
            for node_id in self.cur_nodes:
                self.setNodeChild(node_id,curNode["id"])
                edge = {
                    "id":len(self.data["edges"]),
                    "source":node_id,
                    "target":curNode["id"],
                    "relation":relation,
                    "label":self.condition_label
                }
                self.condition_label = ""
                self.data["edges"].append(edge)
            self.cur_nodes = []
        elif curNode["type"] == "forked":
            self.forked_nodes.append(curNode)

    def addNextNode_v2(self,activities:list):
        condition_no = 0
        for activity in activities:
            if activity["type"] == "condition_no":
                condition_no = 1
                break

        for index, activity in enumerate(activities):
            curNode = activity
            relation = "next"
            if (condition_no == 1 and index == len(activities) - 1):
                curNode["label"] = "endif" + curNode["label"]
            if (index < len(activities)-1 and activities[index+1]["type"] == "condition_no" and condition_no == 1):
                curNode["label"] = "nostop" + curNode["label"]
            if curNode["type"] != "forked":
                if len(self.forked_nodes) != 0:
                    # print(self.forked_nodes)
                    # assert(len(self.forked_nodes)>=2)
                    lastNodeId = len(self.data["nodes"])-1
                    startNode = {
                        "id":len(self.data["nodes"]),
                        "partition":"",
                        "label":"分叉",
                        "type":"fork",
                        "child":[]
                    }
                    edge = {
                        "id":len(self.data["edges"]),
                        "source":lastNodeId,
                        "target":startNode["id"],
                        "relation":"",
                        "label":self.condition_label
                    }
                    self.condition_label = ""
                    self.data["edges"].append(edge)
                    self.data["nodes"].append(startNode)
                    self.setNodeChild(lastNodeId,startNode["id"])
                    endNode = {
                        "id":len(self.data["nodes"]) + len(self.forked_nodes),
                        "partition":"",
                        "label":"连接",
                        "type":"join",
                        "child":[]
                    }
                    for node in self.forked_nodes:
                        node["id"] = len(self.data["nodes"])
                        self.data["nodes"].append(node)
                        if node["partition"] == "":
                            node["partition"] = self.forked_nodes[0]["partition"]
                        self.setNodeChild(startNode["id"],node["id"])
                        edge1 = {
                            "id":len(self.data["edges"]),
                            "source":startNode["id"],
                            "target":node["id"],
                            "relation":"",
                            "label":self.condition_label
                        }
                        self.condition_label = ""
                        self.data["edges"].append(edge1)
                        edge2 = {
                            "id":len(self.data["edges"]),
                            "source":node["id"],
                            "target":endNode["id"],
                            "relation":"",
                            "label":self.condition_label
                        }
                        self.condition_label = ""
                        self.data["edges"].append(edge2)
                    self.data["nodes"].append(endNode)
                    for node in self.forked_nodes:
                        self.setNodeChild(node["id"],endNode["id"])
                    self.forked_nodes = []

            special_types = ["condition_no","merge","forked","condition"]
            if curNode["type"] not in special_types:
                if self.is_connect == 0:
                    startNodeId = len(self.data["nodes"])-1
                    # if len(self.cur_nodes) != 0:
                    #     startNodeId = self.cur_nodes[1]
                else:
                    startNodeId = self.getConditionNodeId()
                    self.is_connect = 0
                if startNodeId == 0 and self.data["nodes"][0]["partition"] == "":
                    self.data["nodes"][0]["partition"] = curNode["partition"]
                if curNode["partition"] == "":
                    curNode["partition"] = self.condition_partition
                    self.condition_partition = ""
                if self.condition_partition != "":
                    self.condition_partition = ""
                curNode["id"] = len(self.data["nodes"])
                self.data["nodes"].append(curNode)
                self.setNodeChild(startNodeId,curNode["id"])
                edge = {
                    "id":len(self.data["edges"]),
                    "source":startNodeId,
                    "target":curNode["id"],
                    "relation":relation,
                    "label":self.condition_label
                }
                self.condition_label = ""
                self.data["edges"].append(edge)
            elif curNode["type"] == "condition":
                # print(curNode)
                self.condition_label = curNode["label"]
                self.condition_partition = curNode["partition"]
                startNodeId = self.getConditionNodeId()
                if startNodeId == len(self.data["nodes"])-1:
                    self.data["nodes"][-1]["type"] = "condition"
                else:
                    if self.compare_str(curNode["label"],self.getConditionEdgeLabel()) >= 0.1:
                        self.is_connect = 1
            elif curNode["type"] == "condition_no":
                startNodeId = self.getConditionNodeId()
                if startNodeId == 0 and self.data["nodes"][0]["partition"] == "":
                    self.data["nodes"][0]["partition"] = curNode["partition"]
                curNode["id"] = len(self.data["nodes"])
                self.data["nodes"].append(curNode)
                self.setNodeChild(startNodeId,curNode["id"])
                edge = {
                    "id":len(self.data["edges"]),
                    "source":startNodeId,
                    "target":curNode["id"],
                    "relation":relation,
                    "label":self.condition_label
                }
                self.condition_label = ""
                self.data["edges"].append(edge)
                self.cur_nodes = [len(self.data["nodes"])-2,len(self.data["nodes"])-1]
            elif curNode["type"] == "merge":
                assert(len(self.data["nodes"])>1)
                curNode["id"] = len(self.data["nodes"])
                self.data["nodes"].append(curNode)
                for node_id in self.cur_nodes:
                    self.setNodeChild(node_id,curNode["id"])
                    edge = {
                        "id":len(self.data["edges"]),
                        "source":node_id,
                        "target":curNode["id"],
                        "relation":relation,
                        "label":self.condition_label
                    }
                    self.condition_label = ""
                    self.data["edges"].append(edge)
                self.cur_nodes = []
            elif curNode["type"] == "forked":
                self.forked_nodes.append(curNode)
 
    def addActivities(self,activities:list):
        # for activity in activities:
        #     self.addNextNode(activity)
        self.addNextNode_v2(activities)

    def getConditionNodeId(self):
        nodes_len = len(self.data["nodes"])
        for i in reversed(range(nodes_len)):
            if self.data["nodes"][i]["type"] == "condition":
                return i
            
        return nodes_len-1
    
    def graph_test(self):
        self.setStartNode()
        activities = [{
            "id":-1,
            "partition":"测试用户",
            "label":"动作节点1",
            "type":"action",
            "child":[]
        },{
            "id":-1,
            "partition":"测试用户",
            "label":"分叉节点1",
            "type":"forked",
            "child":[]
        },{
            "id":-1,
            "partition":"测试用户",
            "label":"分叉节点2",
            "type":"forked",
            "child":[]
        },{
            "id":-1,
            "partition":"测试用户",
            "label":"决策节点",
            "type":"condition",
            "child":[]
        },{
            "id":-1,
            "partition":"测试用户",
            "label":"动作节点2",
            "type":"action",
            "child":[]
        },{
            "id":-1,
            "partition":"测试用户",
            "label":"否则节点",
            "type":"condition_no",
            "child":[]
        },{
            "id":-1,
            "partition":"测试用户",
            "label":"合并节点",
            "type":"merge",
            "child":[]
        },{
            "id":-1,
            "partition":"测试用户",
            "label":"分叉节点1",
            "type":"forked",
            "child":[]
        },{
            "id":-1,
            "partition":"测试用户",
            "label":"分叉节点2",
            "type":"forked",
            "child":[]
        },{
            "id":-1,
            "partition":"测试用户",
            "label":"分叉节点3",
            "type":"forked",
            "child":[]
        }]
        self.addActivities(activities)
        self.setEndNode()