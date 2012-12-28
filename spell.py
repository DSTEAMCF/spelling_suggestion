import re, collections,copy,MySQLdb,time

def words(text): return re.findall('[a-z]+', text.lower()) 

def train():
    model = collections.defaultdict(lambda: 1)
    db = MySQLdb.connect("localhost", "root", "", "dob")
    cursor = db.cursor()
    sql = "select * from us_dob"
    cursor.execute(sql)
    data = cursor.fetchall()
    for row in data:
      model[row[0]] = row[2]
    return model

NWORDS = train()

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def edits1(word):
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return set(deletes + transposes + replaces + inserts)

def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words): return set(w for w in words if w in NWORDS)

def correct(word):
    starttime =  time.clock()
    known_word=known([word])
    edit1_candidates=known(edits1(word))
    # edit2_candidates=known_edits2(word)
    
    score={}
    total_result=[]
    total_result.extend(edit1_candidates)
    # total_result.extend(edit2_candidates)
    
    total_f=0
    
    for w in total_result:
        total_f+=NWORDS.get(w)
        
    # for w in edit2_candidates:
    #     f=NWORDS.get(w)
    #     score[w]=0.1*float(f)/float(total_f*len(edit2_candidates))
    #     print "For edit distance 2:",score
    for w in edit1_candidates:
        f=NWORDS.get(w)
        print f
        score[w]=float(f)/float(total_f*(len(edit1_candidates)))
        print "For edit distance 1:",score
    
    # for w in known_word:
    #     score[w]=1
    
    total_result.extend(known_word)
    total_result=set(total_result)
    # print "score",score
    print "total result:",total_result
    print "top 5 result:"
    print top_result(total_result,5,score)
    print "Best suggestion:",max(total_result,key=score.get)
    stoptime = time.clock()
    print "Time taken:",(stoptime-starttime)
    return top_result(total_result,5,score)
    
def top_result(input,n=5,map=None):
    result=[]
    candidates=copy.deepcopy(input)
    if len(candidates)<n:
        length=len(candidates)
    else:
        length=n
    for i in range(length):
        if map is None:
            best=max(candidates,key=NWORDS.get)
        else:
            best=max(candidates,key=map.get)
        result.append(best)
        candidates.remove(best)
    return result
