#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from d4d import d4d
import sys

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
        def __str__(self):
                return self.title+"\n Description:"+self.s+"\n Tags:"+str(self.tags)+"\n Related Ideas:"+self.print_related_ideas()
        def extract(self):
                self.concepts=extract_concepts(self.description)
        def extend_related_ideas(self,li):
                self.related_ideas.extend(li)
                self.related_ideas.sort(lambda a,b:b[1]-a[1])
        def print_related_ideas(self):
                s=""
                for (i,rel) in self.related_ideas:
                        s=s+str((i.title,rel))
                print s

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
        def __init__(self,db=None):
                self.d={}
                self.ideas_list=[]
                self.related_ideas_dict={}
                self.read_from_file(db)
        def read_from_file(self,db):
                if db!=None:
                        i=1
                        f=open(db,'r')
                        i=read_next_idea(f)
                        while i!=None:
                                self.add(i)
                                i.extract()
                                i=read_next_idea(f)
        def add(self,i):
                #related_ideas=self.get_related_ideas(i)
                #i.extend_related_ideas(related_ideas)
                self.d[i.title]=i
                self.ideas_list.append(i.title)
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
                        s=s+str(i)+" "+title
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

def how_related_are_concept_lists(concept_list1, concept_list2):
        return how_related_are_concept_lists2(concept_list1, concept_list2)

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

if __name__ == '__main__':
        print 'START\n'
##        i1=Idea("Pitch-based scrolling", "e.g. when you sing middle C, the document jumps to 50% mark. natural tool for voice recognition users/RSI/paralyzed patients")
##        i2=Idea("EEG-based Slumping Detector", "What if you could make an app for Google Glasses or similar that follows a person's eyes and then and tracks where they are focusing. This way, you could  compare how different people focus differently, and analyze what that does to their lives. I also imagine that you could you could put on glasses yourself (or watch a screen), and then see the world through another person's eyes. ~jcole@mit.edu")
##        i3=Idea("InstaBoxSite:", "platform to build: generalized, easy to modify \"suggestion box\" framework anyone can use to quickly buildp a website off that mold.  All of following sites and countless more are based on fundamentally the same idea of a \"comments box: isawyou stackoverflow forums reddit fml formspring ideaoverflow.tk / hackathonprojects.tk suggestion box/politicalprogressbar ifiwereanmitstudent.tk tumblr twitter facebook wall. In parallel, I am able to protoype many of the websites I build these days with what is basically a google doc. Why not build a google doc with slightly more functionality that truly allows me to prototype these tools? Check out http://mitdocs.tk/ to see the potential of this. Relatedly, way for people to make a homepage as easily as they can make a google doc -- consider http://adamchu.tk/, and http://minimalisthomepages.tk/  ~jcole@mit.edu")
        db=Database("idea_db.txt")
##        db.extend([i1,i2,i3])
##        print getRelatedIdeas(Idea('eeg scrolling','eeg scrolling'))
        while True:
                print db
                s=raw_input()
                if s=="":
                        break
                else:
                        i=int(s)
                        if db[i].populated==False:
                                db.populate_related_ideas(i)
                        db[i].print_related_ideas()
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
