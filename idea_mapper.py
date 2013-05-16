#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from d4d import d4d
import sys
from csc import divisi2

class Idea:
        def __init__(self,title="",text="",tags=""):
                self.title=title
                self.description=text
                self.problem=""
                self.solution=""
                self.technology=""
                self.tags=tags
                #extract concepts from idea and store them
                self.extract()
                #print "concepts: ",self.concepts
                self.related_ideas=[]
                #maybe add an idea ID number
                self.populated=False
                self.ID=0
        def setID(self, i):
                self.ID=i
        def __str__(self):
                return self.title+"\n Description:"+self.description+"\n Tags:"+str(self.tags)+"\n Related Ideas:"+self.print_related_ideas()
        def extract(self):
                self.concepts=extract_concepts(self.description)
        def extend_related_ideas(self,li):
                self.related_ideas.extend(li)
                self.related_ideas.sort(lambda a,b:b[1]-a[1])
        def print_related_ideas(self):
                s=""
                for (i,rel) in self.related_ideas:
                        s=s+str(i.ID)+" "+i.title[:-1]+": "+i.description[0:50]+" "+str(rel)+"\n"
                return s

def read_next_idea(f):
        i=Idea()
        prev_field=None
        cur_string=""
        s=f.readline()
        if s=="\n":
                return None
        while True:
                if s=="\n":
                        #print "updating ",prev_field," with ",cur_string
                        globals().update([[prev_field,cur_string]])
                        break
                new_field=which_field(s)
                #print "New:", new_field
                #print "String:",cur_string
                if new_field!=None:
                        if prev_field!=None:
                                #print "updating ",prev_field," with ",cur_string
                                globals().update([[prev_field,cur_string]])
                        cur_string=s[len(new_field)+1:]
                        new_field=new_field[:-1].lower()
                        prev_field=new_field
                else:
                        cur_string=cur_string+s
                s=f.readline()
        #there should be an easier way to do this
        i.title=title
        i.description=description
        i.problem=problem
        i.solution=solution
        i.technology=technology
        i.tags=tags
        return i

def which_field(s):
        fields=["TITLE:","DESCRIPTION:", "MORE:", "PROBLEM:", "SOLUTION:", "TECHNOLOGY:", "TAGS:"]
        for f in fields:
                if s[0:len(f)]==f:
                        return f
        return None

class Database:
        def __init__(self,db=None,mat_string=None):
                self.d={}
                self.ideas_list=[]
                self.related_ideas_dict={}
                self.read_from_file(db)
                #create a sparse matrix from ideas.
                if mat_string==None:
                        self.idea_matrix=divisi2.SparseMatrix.square_from_named_entries([(0,0,0)])
                else:
                        self.idea_matrix=divisi2.load(mat_string)
        def read_from_file(self,db):
                if db!=None:
                        i=1
                        self.f=open(db,'a+')
                        i=read_next_idea(self.f)
                        while i!=None:
                                self.add(i)
                                i.extract()
                                i=read_next_idea(self.f)
        #i,j are indices to ideas
        def connect_ideas(self,i,j):
                mat=divisi2.SparseMatrix.square_from_named_entries([(1,i,j),(1,j,i)])
                self.idea_matrix=self.idea_matrix+mat
        def find_ideas_with_common_friends(self,i,num_friends=5):
                #normalize each row
                normalized=self.idea_matrix.squish().normalize_rows()                
                #find the row
                row=normalized[i]
                a=normalized.dot(row)
                #nbs=row.dot(normalized.transpose())
                maxV=0
                maxI=0
                b=sorted(a.entries(),reverse=True)                        
                for i in xrange(min(5,len(b))):
                        idea= self[b[i][1]]#print the idea
                        print idea.ID, " ", idea.title[:-1], ", ", b[i][0]
        def add(self,i,add_to_file=False):
                #related_ideas=self.get_related_ideas(i)
                #i.extend_related_ideas(related_ideas)
                self.d[i.title]=i
                self.ideas_list.append(i.title)
                i.ID=len(self.ideas_list)-1
                if add_to_file:
                        f.write("TITLE: "+i.title+"\nDESCRIPTION: "+i.description+\
                                "\nMORE: "+i.more+"\nPROBLEM: "+i.problem+"\nSOLUTION: "+\
                                "\nTECHNOLOGY: "+i.technology+"\nTAGS: "+i.tags+"\n\n")
        def extend(self, li):
                for i in li:
                        self.add(i)
        def populate_related_ideas(self, i):
                li=self.get_related_ideas(self[i],False)
                self[i].related_ideas=li
                self[i].related_ideas.sort(lambda a,b:signum(b[1]-a[1]))
                self[i].populated=True
        def populate_all_related_ideas(self):
                for i in self.d.values():
                        populate_related_ideas(i)
        def __getitem__(self,i):
                if type(i)==str:
                        return self.d[i]
                #index by id too? Maybe this is not necessary.
                elif type(i)==int:
                        return self.d[self.ideas_list[i]]
                return
        def how_related_are_ideas(self,idea1,idea2):
                return how_related_are_concept_lists(idea1.concepts, idea2.concepts)
        #how do we compute this?
        def get_related_ideas(self,qidea,allow_repeat=True):
                #idea already has extracted concepts stored
                relatedness = []
                for i in self.d.values():
                        if (allow_repeat or i!=qidea):
                                relatedness.append((i, self.how_related_are_ideas(qidea,i)))
                return sorted(relatedness, reverse=True)
                #list truncated to top 5
        def __str__(self):
                s=""
                for (i,title) in enumerate(self.ideas_list):
                        s=s+str(i)+" "+title+"   "+self[i].description
                return s
        

def extract_concepts(idea):
        a=d4d.en_nl.extract_concepts(idea, check_conceptnet=True)
        #print "Extracting from ",idea
        #print "Concepts extracted: ",a
        return a# max_words=2, check_conceptnet=True)

def signum(a):
        if a>0:
                return 1
        if a<0:
                return -1
        return 0
'''
calculates how related two concepts are
'''
def how_related_are(concept1, concept2):
        #print concept1, concept2
        try:
                return d4d.d4d.c4.how_related_are(concept1, concept2)
        except KeyError: # key does not exist
                #print "key error ",concept1," ",concept2
                return 0

def how_related_are_concept_lists(concept_list1, concept_list2, metric_num=2):
        s="how_related_are_concept_lists"+str(metric_num)
        return globals()[s](concept_list1, concept_list2)

#first implementation: take top 5 relationships
def how_related_are_concept_lists1(concept_list1, concept_list2):
        """returns numerical relationship level 0 and up"""
        maxVs=[0,0,0,0,0]
        maxCs=[('',''),('',''),('',''),('',''),('','')]
        
        for c1 in concept_list1:
                for c2 in concept_list2:
                        r=how_related_are(c1, c2)
                        if r>maxVs[0]:
                                maxVs[0] = r
                                #maxVs.insert(0,r)
                                #maxCs.insert(0,(c1,c2))
                                #maxVs.pop()
                                #maxCs.pop()
                                maxVs.sort()

        #print maxCs
        return sum(maxVs)

#second implementation: take top relationships with each concept in the first list,
#and normalize
def how_related_are_concept_lists2(concept_list1, concept_list2):
        #print "lists: ",concept_list1,concept_list2
        maxVs=[]#0,0,0,0,0]
        maxCs=[]#('',''),('',''),('',''),('',''),('','')]
        for c1 in concept_list1:
                maxV=0
                maxC=('','')
                for c2 in concept_list2:
                        #print (c1,c2)
                        r=how_related_are(c1, c2)
                        if r>maxV:
                                maxV = r
                                maxC=(c1,c2)
                maxVs.append(maxV)
                maxCs.append(maxC)
        #print maxCs
        total=sum(maxVs)/len(concept_list1)
        maxes=zip(maxVs,maxCs)
        maxes.sort(reverse=True)
        for (r,(c1,c2)) in maxes:
                print r," ",(c1,c2)
        print "-------------"
        print "Total: ",total
        return total

#third implementation: multiply idea vector by AA^T by idea vector 2, where
#A is concepts*features matrix.
##def how_related_are_concept_lists3(concept_list1, concept_list2):
##        #remove duplicates
##        concept_list1 = list(set(concept_list1))
##        concept_list2 = list(set(concept_list2))
##        len1=len(concept_list1)
##        len2=len(concept_list2)
##        if len1==0 or len2==0:
##                return 0
##        v1=[1/math.sqrt(len1) for i in concept_list1]
##        v2=[1/math.sqrt(len2) for i in concept_list2]
##        sv1=divisi2.SparseVector.from_lists(v1, concept_list1)
##        sv2=divisi2.SparseVector.from_lists(v2, concept_list2)
##        sv1.to_row().dot(
##        #
##        for (r,(c1,c2)) in maxes:
##                print r," ",(c1,c2)
##        print "-------------"
##        print "Total: ",total
##        return total

def list_ideas(db):
        print db
##def add_new(db):
##        title = raw_input("Enter idea title: ")
##        text = raw_input("Enter idea text: ")
##        print "Creating idea ",title
##        new_idea=Idea(title,text)
##        db.add(new_idea)
##        db.populate_related_ideas(len(db.ideas_list)-1)
##        print "Concepts in idea: ",str(new_idea.concepts)
##        print "Related ideas: ",new_idea.print_related_ideas()
def add_new(db):
        title = raw_input("Enter idea title: ")
        text = raw_input("Enter idea text: ")
        new_idea=Idea(title,text)
        db.add(new_idea)
        idea_id=len(db.ideas_list)-1
        db.populate_related_ideas(idea_id)
        #print "Concepts in idea: ",str(new_idea.concepts)
        print "Related ideas: ",new_idea.print_related_ideas()
        while True:
                s=raw_input("Make relations with: ")
                if s=="":
                        break
                l=s.split(" ")
                for i in l:
                        db.connect_ideas(idea_id,int(i))
                print "Related idea suggestions:"
                db.find_ideas_with_common_friends(idea_id)
def connect(db):
        id1 = int(raw_input("Idea 1 ID: "))
        id2 = int(raw_input("Idea 2 ID: "))
        db.connect_ideas(id1,id2)
def find_related_idea(db):
        s=raw_input()
        if s=="":
                pass
        else:
                i=int(s)
                if db[i].populated==False:
                        db.populate_related_ideas(i)
                print db[i].print_related_ideas()
def find_friend_idea(db):
        s=int(raw_input("Idea ID:"))
        db.find_ideas_with_common_friends(s)
def add_category(db):
        pass
def save(db):
        divisi2.save(db.idea_matrix,"idea_mat.pickle")
def load(db):
        db.idea_matrix=divisi2.load("idea_mat.pickle")
def display_reln(db):
        print db.idea_matrix
def quit_program(db):
        sys.exit(0)

logic={0:"List ideas ",1:"Add new ",2: "Establish connection",\
       3:"Find related ideas using conceptnet", 4:"Find related ideas using mutual connections",\
       5:"Add category", 6: "Save", 7:"Load", 8:"Display relationships",9:"Quit"}
logic2={0:list_ideas, 1:add_new, 2:connect,\
       3:find_related_idea, 4:find_friend_idea,\
       5:add_category, 6:save, 7:load,8:display_reln,9:quit_program}

if __name__ == '__main__':
        print 'START\n'
##        i1=Idea("Pitch-based scrolling", "e.g. when you sing middle C, the document jumps to 50% mark. natural tool for voice recognition users/RSI/paralyzed patients")
##        i2=Idea("EEG-based Slumping Detector", "What if you could make an app for Google Glasses or similar that follows a person's eyes and then and tracks where they are focusing. This way, you could  compare how different people focus differently, and analyze what that does to their lives. I also imagine that you could you could put on glasses yourself (or watch a screen), and then see the world through another person's eyes. ~jcole@mit.edu")
##        i3=Idea("InstaBoxSite:", "platform to build: generalized, easy to modify \"suggestion box\" framework anyone can use to quickly buildp a website off that mold.  All of following sites and countless more are based on fundamentally the same idea of a \"comments box: isawyou stackoverflow forums reddit fml formspring ideaoverflow.tk / hackathonprojects.tk suggestion box/politicalprogressbar ifiwereanmitstudent.tk tumblr twitter facebook wall. In parallel, I am able to protoype many of the websites I build these days with what is basically a google doc. Why not build a google doc with slightly more functionality that truly allows me to prototype these tools? Check out http://mitdocs.tk/ to see the potential of this. Relatedly, way for people to make a homepage as easily as they can make a google doc -- consider http://adamchu.tk/, and http://minimalisthomepages.tk/  ~jcole@mit.edu")
        db=Database("idea_db.txt")
##        db.extend([i1,i2,i3])
##        print getRelatedIdeas(Idea('eeg scrolling','eeg scrolling'))
        while True:
                for k in logic:
                        print k," ",logic[k]
                a=int(raw_input())
                logic2[a](db)
                        
##                #warning: don't create duplicates
##                title = raw_input("Enter idea title: ")
##                if title=="":
##                        sys.exit(0)
##                text = raw_input("Enter idea text: ")
##                print "Creating idea ",title
##                new_idea=Idea(title,text)
##                db.add(new_idea)
##                db.populate_related_ideas(len(db.ideas_list)-1)
##                print "Concepts in idea: ",str(new_idea.concepts)
##                print "Related ideas: ",new_idea.print_related_ideas()
