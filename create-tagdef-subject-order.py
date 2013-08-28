from __future__ import print_function
import random
import string
import os
import sys
import time 
import tagfiler_client

goauth_token = sys.argv[1]
catalogid = int(sys.argv[2])
tagdefstart = int(sys.argv[3])
tagdefend = int(sys.argv[4])
subjectstart = int(sys.argv[5])
subjectend = int(sys.argv[6])
subjectrange = int(sys.argv[7])
randmax = int(sys.argv[8])

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
   '''For sleep time
   def counter(self):
        self.count = self.count + 1
        return self.count
   def getcounter(self):
        print self.count
        return
   '''	
def id_gen_upp(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def enum_subjects(st,rng,tst,tend):
        subjects = []
        for i in xrange(st,st+rng):
	   seq = (('test%d' % j) for j in range(tend-1,tst-1,-1))
	   subject = collections.OrderedDict()
           subject.fromkeys(seq)
           subject.update({'test0':('%s_%d' % (id_gen_upp(random.randint(0,randmax)),i))})
	   for j in range(tst,tend):
              subject[('test%d' % j)] = '%s' % id_gen_upp(random.randint(0,randmax))
           subjects.append(subject) 
	print subjects
	return subjects
try:
    os.remove("tagdef_time_ord")
    os.remove("subject_time_ord")
except OSError:
    pass



tagclient.create_tagdef(catalogid,'test0', "text", False,True)
for i in range(tagdefstart,tagdefend):
    with open("tagdef_time_ord",'a') as f1:
       with Timer(f1):
          tagclient.create_tagdef(catalogid,("test%s" % i), "text", True, False)
          #print('Create_tagdef %d test%d', catalogid, i,file=f1) 
       time.sleep(1.0)
print("Tagdef creation finish")


while (subjectstart < subjectend):
    with open("subject_time_ord",'a') as f2:
       with Timer(f2):
          tagclient.create_subjects(catalogid, enum_subjects(subjectstart,subjectrange,tagdefstart,tagdefend),'test0')
    subjectstart = subjectstart +subjectrange
    print("Subject batch creation finish")
    time.sleep(1.0)



