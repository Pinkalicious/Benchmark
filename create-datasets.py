'''
This program will create datasets where a dataset = a directory heirarchy, metadata in key-value pairs at the directory root, and metadata in key-value pairs onfiles. Some intermediate nodes may also be assigned metadata of the root, with changed values.

Datasets belong to a single application domain so the metadata will not change across dataset directories. At the file level, some metadata will change.
'''

from __future__ import print_function
import random
import string
import os
import copy
import sys
import time
import tagfiler_client

(_ADD, _DELETE, _INSERT) = range(3)
(_ROOT, _DEPTH, _WIDTH) = range(3)

randmax = 10
cfg= {"maxDepth" : 3,"maxChildren":3,"maxMembers":8,"independent":1,"gauss":2,"mu":1.0,"sigma":0.5}
dsType = ['int8','boolean','float8','timestamptz','date','text']
dsMultival = ['0','1']

goauth_token = sys.argv[1]
catalogid = 13 #int(sys.argv[2])
dsstart = 0 #int(sys.argv[3])
dsend = 1 #int(sys.argv[4])

tagclient = tagfiler_client.TagfilerClient(goauth_token)


class Timer():
   #count = 0;
   filename = None
   def __init__(self,f):
        self.filename = f
   def __enter__(self):
        self.start = time.time()
   def __exit__(self, *args):
        print (time.time() - self.start,file=self.filename)



class Node():
    def __init__(self, name, expanded=True):
        self.name = name
        self.expanded = expanded
        self.name = name
        self.expanded = expanded
        self.__identifier = sanitize_id(self.name)
        self.__bpointer = None
        self.__fpointer = []
        self.__cntMembers = 0
        self.subjectID = 0
        self.__dbId = 0
        self.__tagdefList = []
        self.__filetagdefList = []

    @property
    def identifier(self):
        return self.__identifier

    @property
    def cntMembers(self):
        return self.__cntMembers

    @cntMembers.setter
    def cntMembers(self,value):
        if value is not None:
            self.__cntMembers = value

    @property
    def dbId(self):
        return self.__dbId

    @dbId.setter
    def dbId(self,value):
        if value is not None:
            self.__dbId = value

    @property
    def bpointer(self):
        return self.__bpointer

    @bpointer.setter
    def bpointer(self, value):
        if value is not None:
            self.__bpointer = sanitize_id(value)

    @property
    def fpointer(self):
        return self.__fpointer

    def tagdefList(self):
        return self.__tagdefList

    def tagdefList(self,value):
        if value is not None:
            self.__tagdefList = value

    def filetagdefList(self):
        return self.__filetagdefList

    def filetagdefList(self,value):
        if value is not None:
            self.__filetagdefList = value

    def update_fpointer(self, identifier, mode=_ADD):
        if mode is _ADD:
            self.__fpointer.append(identifier)
        elif mode is _DELETE:
            self.__fpointer.remove(identifier)
        elif mode is _INSERT:
            self.__fpointer = [identifier]

class Tree:
    def __init__(self,depth):
        self.depth = depth
        self.nodes = []


    def get_index(self, position):
        for index, node in enumerate(self.nodes):
            if node.identifier == position:
                break
        return index

    def create_node(self, name, identifier=None, parent=None):
        """Create a child node for the node indicated by the 'parent' parameter"""

        node = Node(name, identifier)
        self.nodes.append(node)
        self.__update_fpointer(parent, node.identifier, _ADD)
        node.bpointer = parent
        return node

    def move_node(self, source, destination):
        """
        Move a node indicated by the 'source' parameter to the parent node
                      indicated by the 'dest' parameter
        """
        pass

    def remove_node(self, identifier):
        pass

    def show(self, position, level=_ROOT):
        queue = self[position].fpointer
        if level == _ROOT:
            print("{0} [{1}]".format(self[position].name,
                                     self[position].identifier))
        else:
            print("t"*level, "{0} [{1}]".format(self[position].name,
                                                 self[position].identifier))
        if self[position].expanded:
            level += 1
            for element in queue:
                self.show(element, level)  # recursive call

    def is_branch(self, position):
        return self[position].fpointer

    def __update_fpointer(self, position, identifier, mode):
        if position is None:
            return
        else:
            self[position].update_fpointer(identifier, mode)

    def __update_bpointer(self, position, identifier):
        self[position].bpointer = identifier

    def __getitem__(self, key):
        return self.nodes[self.get_index(key)]

    def __setitem__(self, key, item):
        self.nodes[self.get_index(key)] = item

    def __len__(self):
        return len(self.nodes)

    def __contains__(self, identifier):
        return [node.identifier for node in self.nodes
                if node.identifier is identifier]

def sanitize_id(value):
    return value.strip().replace(" ", "")

def id_generator_upper(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def id_generator_lower(size=6, chars=string.ascii_lowercase):
    return ''.join(random.choice(chars) for x in range(size))

def create_dataset(currDepth,tree,index,parent):
    print('     CurrDepth %d TreeDepth: %d', currDepth,tree.depth)
    if  (currDepth < tree.depth):
        name = "Dataset." + index
        print("Name: %s ", name)
        node = tree.create_node(name,name,parent)
        if (tree.depth > 1) and (currDepth < tree.depth-1):
            children = random.randint(1,cfg.get("maxChildren"))
            print("     Children %d", children)
            currDepth = currDepth + 1
            for j in range(0,children):
                create_dataset(currDepth,tree,(index + "." +str(j)),node)
        else:
            node.cntMembers = random.randint(0,cfg.get("maxMembers"))
            print("         File members %d", node.cntMembers)
    else:
        if (currDepth > 0):
            parent.cntMembers = random.randint(0,cfg.get("maxMembers"))
            print("         File members %d", parent.cntMembers)
            return
    return name,tree.depth

def enum_subjects(st,rng,tagdefs,unq_name):
        subjects = []
        for i in xrange(st,st+rng):
           seq = (tagdefs[j].get('name') for j in range(0,len(tagdefs)))
           subject = dict.fromkeys(seq)
           subject.update({unq_name:('%s_%d' % (id_generator_lower(random.randint(0,randmax)),i))})
           for j in range(1,len(tagdefs)):
              if (tagdefs[j].get('name') != unq_name):
                 subject[tagdefs[j].get('name')] = '%s' % id_generator_upper(random.randint(0,randmax))
              subjects.append(subject)
        return subjects

def getTagdefs(gbID,unq_name,tagdefList=None,mode=None):
    tList = []
    if (mode == cfg.get("independent")):
        tList = [{'name':unq_name,'type':'text','multival':"0",'unique':"1"}]
    elif (mode == cfg.get("gauss")):
        tList = tagdefList

    cnt1 = random.randint(10,15)
    cnt2 = random.randint(0,3)
    name=""
    if (mode == cfg.get("independent")):
        for i in range(1,cnt1):
            #Nice to have different types
            #dtype = dsType[random.randint(0,len(dsType)-1)]
            tDict = {}
            tDict['name'] = 'test%d_%d' % (gbID,i)
            tDict['type'] =  "text"
            tDict['multival'] = dsMultival[random.randint(0,1)]
            tDict['unique'] = "False"
            tList.append(tDict)
    elif (mode == cfg.get("gauss")):
        for i in range(1,cnt2):
            idx = random.randint(1,len(tList)-1)
            name = 'test%d_%d' % (gbID,i)
            elem = tList[idx]
            elem['name'] = name
    return tList

try:
    os.remove("dataset_tagdef_time")
    os.remove("dataset_subject_time")
except OSError:
    pass

# dataset and static file tagdefs once for an application
gbID = 1
dsTagdefs = getTagdefs(gbID,'ds_name',None,"independent")

gbID = gbID + 1
staticfileTagdefs = getTagdefs(gbID,'fs_name',None,"independent")

with open("dataset_tagdef_time",'a') as f1:
    with Timer:
        for j in range(0,len(dsTagdefs)):
            tagclient.create_tagdef(catalogid,dsTagdefs[j].get('name'),dsTagdefs[j].get('type'),dsTagdefs[j].get('multival'),dsTagdefs[j].get('unique'))

        for j in range(0,len(staticfileTagdefs)):
            tagclient.create_tagdef(catalogid,staticfileTagdefs[j].get('name'),staticfileTagdefs[j].get('type'),staticfileTagdefs[j].get('multival'),dsTagdefs[j].get('unique'))

for dsid in range(dsstart,dsend,1):
        fileTagdefs = staticfileTagdefs
        if (random.randint(0,1)):
                gbID = gbID + 1
                fileTagdefs = getTagdefs(gbID,'fs_name',copy.deepcopy(staticfileTagdefs),'gauss')
                a = set(fileTagdefs[j].get('name') for j in range(0,len(fileTagdefs)))
                b = set(staticfileTagdefs[j].get('name') for j in range(0,len(staticfileTagdefs)))
                diffTagdefs = list(a-b)

        dsTree = Tree(random.randint(1,cfg.get("maxDepth")))
        name,depth = create_dataset(0,dsTree,str(dsid),None)
    
        with open("subject_tagdef_time",'a') as f1:
            with Timer:
                for i in range(0,len(dsTree.nodes)):
                    if (i == 0): #Root
                        for j in range(0,len(diffTagdefs)):
                            tagclient.create_tagdef(catalogid,diffTagdefs[j].get("name"),diffTagdefs[j].get("type"),diffTagdefs[j].get("multival"),False)
    
                        tagclient.create_subjects(catalogid,enum_subjects(str(dsid),1,dsTagdefs,'ds_name'),'ds_name')
                    else: # intermediate node
                        print('Create Intermediate Node %s') % dsTree.nodes[i].name
                        #create_dataset_subject(catalogId,tree.nodes[i],None)
                    if (dsTree.nodes[i].cntMembers > 0): #leaf node
                            tagclient.create_subjects(catalogid,enum_subjects(0,dsTree.nodes[i].cntMembers,fileTagdefs),'fs_name')
