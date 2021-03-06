import time
import random #use random.choice(list) to get random elt from list
import glob
import copy
#TODO this is broekn with multiple clip managers. need to give each one an id
def getTimeOnFrame(state):
    return time.time()-state["time_enter_frame"]
def getSubset(aset,idlist):
    #make sure idlist is a LIST not a string
    #todo make sure this does not return one element twice
    s = list()
    for e in idlist:
        for f in aset:
            if e in f[0]:
                s.append(f)
    return s
    
def removeElementFromSet(aset,elt):
    for e in aset:
        if e[1] == elt:
            aset.remove(e)
            break
        
def saveMemory(state,frame):
    if "MEMORY" in state:
        del state["MEMORY"]
    memory = (dict(state),frame)
    memory[0]["visited"] = copy.deepcopy(state["visited"])
    state["MEMORY"] = memory
    print "memory saved", memory
    
def loadMemory(state):
    if "MEMORY" in state:
        memory = state["MEMORY"]
    else:   #this case should not happen
        print "resetting game"
        state["RESET"] = 0
        return "-1"
    return memory

def init_graph(state):
    glob.sound.loadSound("jake_FINAL/sound/click.aiff")
    glob.sound.loadSound("jake_FINAL/sound/garand_shoot_fire.wav")
    glob.sound.loadSound("jake_FINAL/sound/victory2.aiff")
    state["time_enter_frame"] = time.time()
    state["first_shot"] = True
    state["first_hesitate"] = True
    state["eyes_open"] = True
    #(category, name)
    state["visited"] = list([
                        ("FH1",u"FH1_1"),
                        ("FH1",u"FH1_2"),
                        ("FH1",u"FH1_3"),
                        ("FH2",u"FH2_1"),
                        ("FH2",u"FSFH2_2"),
                        ("FH2",u"FSFH2_3"),
                        ("FY",u"FY_1"),
                        ("Bgoesfirst",u"Bgoesfirst_1"),
                        ("Bgoesfirst",u"Bgoesfirst_2"),
                        ("Bgoesfirst",u"Bgoesfirst_3"),
                        ("BshootsB",u"BshootsB_1"),
                        ("BshootsB",u"BshootsB_2"),
                        ("Btakesgun",u"Btakesgun_1"),
                        ("Btakesgun",u"Btakesgun_2"),
                        ("Bdies",u"Bdies_1"),
                        ("Bdies",u"Bdies_2"),
                        ("Bdies",u"Bdies_3"),
                        ("Bdies",u"Bdies_4"),
                        ("Bdies",u"Bdies_5"),
                        ("FY",u"FY_2"),
                        ("FY",u"FY_3"),
                        ("DH",u"DH_1"),
                        ("DH",u"DH_2"),
                        ("DH",u"DH_3"),
                        ("YT",u"YT_1"),
                        ("YT",u"YT_2"),
                        ("YT",u"YT_3"),
                        ("SH1",u"SH1_1"),
                        ("SH1",u"SH1_2"),
                        ("SH1",u"SH1_3"),
                        ("SH2",u"SH2_1"),
                        ("SH2",u"SH2_2"),
                        ("SH2",u"SH2_3"),
                        ("lucky",u"lucky_1"),
                        ("lucky",u"lucky_2"),
                        ("lucky",u"lucky_3"),
                        ])
    
def on_new_frame(state):
    state["time_enter_frame"] = time.time()
def blink(state,clip):
    if clip.getTimeLeft() < 0.2:
        state["blinking"] = True
def youlose(state,clip):
    glob.sound.play("jake_FINAL/sound/garand_shoot_fire.wav")
    return "continue"
def stupid(state,clip,chance = 1):
    return not bool(random.randint(0,chance))
def graph_default(state,clip):
    return -1
def graph_start(state,clip):
    if state["press"]:
        state["fade"] = 1
    if state["fade"] == 1 and time.time() - state["time_pressed"] > 1.3:
        return "intro"
    else: return "-1"
def graph_wait(state,clip):
    blink(state,clip)
    if state["lose"]:
        return youlose(state,clip)
    if state["player_shoot_state"] == 2:
        state["player_shoot_state"] = 0
        if stupid(state,clip):
            return random.choice(["funny_lucky","crowdgoeswild"])
        return random.choice(getSubset(state["visited"],["lucky",]))[1]
    if state["turn"] == "B" and state["player_shoot_state"] == 0:
        return random.choice(getSubset(state["visited"],["Btakesgun",]))[1]
    if clip.isFinished():
        #this will make sure we wont transition into anything bad when player is shooting
        if state["player_shoot_state"] == 0:
            if state["first_hesitate"]:
                if state["FH_state"] == 0:
                    return random.choice(getSubset(state["visited"],["FH1",]))[1]
                elif state["FH_state"] == 1:
                    if not state["first_shot"]:
                        return random.choice(getSubset(state["visited"],["SH1",]))[1]      
                    return random.choice(getSubset(state["visited"],["FH2",]))[1]
                elif state["FH_state"] == 2:
                    state["turn"] = "B" 
                    state["first_shot"] = False
                    state["first_hesitate"] = False
                    return random.choice(getSubset(state["visited"],["Bgoesfirst",]))[1]
            else:    #second hesitate
                return random.choice(getSubset(state["visited"],["SH1",]))[1]      
        return "wait"
    return "-1"
def graph_leantowait(state,clip):
    blink(state,clip)
    if clip.isFinished():
        return "wait"
    else: return "-1"
def graph_waitlean(state,clip):
    blink(state,clip)
    if state["lose"]:
        return youlose(state,clip)
    if state["player_shoot_state"] == 2:
        state["player_shoot_state"] = 0
        return "leantowait"
    if clip.isFinished():
        if state["SH_state"] == 0:
            state["SH_state"] = 1
            return random.choice(getSubset(state["visited"],["SH2",]))[1]
        elif state["SH_state"] == 1:
            if state["player_shoot_state"] == 0:
                state["turn"] = "B" 
                state["SH_state"] = 0
                if stupid(state,clip,500) and state["shots_fired"] < 5:
                    state["shots_fired"] += 1
                    return random.choice(["sideways_1","sideways_2"])
                return "SH3"
            return "waitlean"
    else: return "-1"
    
def graph_intro(state,clip):
    blink(state,clip)
    if clip.getTime() > 3:
        state["fade"] = 0
    if clip.isFinished():
        #we allow player to shoot himself now
        state["turn"] = "Y" 
        #TODO fix this
        saveMemory(state,"wait")
        return "wait"
    else: return "-1"
    
def FH_generic(state,clip,name):
    blink(state,clip)
    if state["lose"]:
        return youlose(state,clip)
    if clip.isFinished():
        #remove the element because we've been there already
        removeElementFromSet(state["visited"],name) 
        #advance state
        state["FH_state"] += 1
        return "wait"
    else: return "-1"
def graph_FH1_1(state,clip):
    return FH_generic(state,clip,"FH1_1")
def graph_FH1_2(state,clip):
    return FH_generic(state,clip,"FH1_2")
def graph_FH1_3(state,clip):
    return FH_generic(state,clip,"FH1_3")
def graph_FH2_1(state,clip):
    state["first_shot"] = False
    return FH_generic(state,clip,"FH2_1")
def graph_FSFH2_2(state,clip):
    state["first_shot"] = False
    return FH_generic(state,clip,"FSFH2_2")
def graph_FSFH2_3(state,clip):
    state["first_shot"] = False
    return FH_generic(state,clip,"FSFH2_3")
def Bgoesfirst_generic(state,clip,name):
    blink(state,clip)
    if clip.isFinished():
        removeElementFromSet(state["visited"],name) 
        return random.choice(getSubset(state["visited"],["Btakesgun",]))[1]
    else: return "-1"
def graph_Bgoesfirst_1(state,clip):
    return Bgoesfirst_generic(state,clip,"Bgoesfirst_1")
def graph_Bgoesfirst_2(state,clip):
    return Bgoesfirst_generic(state,clip,"Bgoesfirst_2")
def graph_Bgoesfirst_3(state,clip):
    return Bgoesfirst_generic(state,clip,"Bgoesfirst_3")
def graph_FH4(state,clip):
    blink(state,clip)
    if clip.isFinished(): return "BshootsY"
    else: return "-1"
    
def Btakesgun_generic(state,clip,name):
    blink(state,clip)
    #TODO check gun condition first, and potentially send to BshootsB_1/2 
    if clip.isFinished():
        #=======================================================================
        # #if live and fifty fifty
        # if random.randint(0,1) == 0:
        #    if random.randint(0,5) > state["shots_fired"]-1:
        #        state["shots_fired"] += 1
        #        return random.choice(getSubset(state["visited"],["BshootsB",]))[1]
        #    #if we fail test, we put shots to 6 so B will die next shot no matter what :(
        #    else: 
        #        state["shots_fired"] = 6
        #        return "BshootsB_cut"
        #=======================================================================
        #removeElementFromSet(state["visited"],name) #not going to work since we only have 2 clips but this gets called maybe 3 times
        #we just skip this step it's not too important 
        return "BshootsB_cut"
    else: return "-1"
    
def graph_Btakesgun_1(state,clip):
    return Btakesgun_generic(state,clip,"Btakesgun_1")
def graph_Btakesgun_2(state,clip):
    return Btakesgun_generic(state,clip,"Btakesgun_2")
    
def graph_BshootsY(state,clip):
    blink(state,clip)
    if clip.isFinished():
        state["shots_fired"] += 1
        if random.randint(0,5) <= state["shots_fired"]-1:
            return youlose(state,clip) 
        else:
            return "FY"
    else: return "-1"
    
def graph_FY(state,clip):
    blink(state,clip)
    if clip.isFinished():
        return "BshootsB_cut"
    else: return -1
def FY_generic(state,clip,name):
    blink(state,clip)
    if clip.isFinished():
        removeElementFromSet(state["visited"],name) 
        return "BprepareshootB"
    else: return "-1"
def graph_FY_1(state,clip):
    return FY_generic(state,clip,"FY_1")
def graph_FY_2(state,clip):
    return FY_generic(state,clip,"FY_2")
def graph_FY_2(state,clip):
    return FY_generic(state,clip,"FY_3")

def graph_BprepareshootB(state,clip):
    blink(state,clip)
    if clip.isFinished(): 
        return random.choice(getSubset(state["visited"],["DH",]))[1]
    else: return "-1"
    
def DH_generic(state,clip,name):
    blink(state,clip)
    if clip.isFinished():
        #remove the element because we've been there already
        removeElementFromSet(state["visited"],name) 
        #advance state
        return "BshootsB"
    else: return "-1"
def graph_DH_1(state,clip):
    return DH_generic(state,clip,"DH_1")
def graph_DH_2(state,clip):
    return DH_generic(state,clip,"DH_2")
def graph_DH_3(state,clip):
    return DH_generic(state,clip,"DH_3")

def BshootsB_generic(state,clip,name):
    blink(state,clip)
    if clip.isFinished():
        #removeElementFromSet(state["visited"],name) 
        return "wait"
        #=======================================================================
        # state["shots_fired"] += 1
        # if random.randint(0,5) <= state["shots_fired"]-1:
        #    return random.choice(getSubset(state["visited"],["Bdies",]))[1]
        # else:
        #    state["turn"] = "Y"
        #    return random.choice(getSubset(state["visited"],["YT",]))[1]
        #=======================================================================
    else: return "-1"
def graph_BshootsB_1(state,clip):
    return BshootsB_generic(state,clip,"BshootsB_1")
def graph_BshootsB_2(state,clip):
    return BshootsB_generic(state,clip,"BshootsB_2")
def graph_BshootsB_cut(state,clip):
    blink(state,clip)
    if clip.isFinished():
        state["shots_fired"] += 1
        if random.randint(0,5) <= state["shots_fired"]-1:
            glob.sound.play("jake_FINAL/sound/garand_shoot_fire.wav")
            return random.choice(getSubset(state["visited"],["Bdies",]))[1]
        else:
            state["turn"] = "Y"
            glob.sound.play("jake_FINAL/sound/click.aiff")
            if stupid(state,clip): return "blowgun"
            return random.choice(getSubset(state["visited"],["YT",]))[1]
    else: return "-1"
def Bdies_generic(state,clip,name):
    if clip.getTimeLeft() < 15 and clip.getTimeLeft() > 14.5:
        if stupid(state,clip,100):
            if not glob.sound.isPlaying("jake_FINAL/sound/victory2.aiff"):
                glob.sound.play("jake_FINAL/sound/victory2.aiff")
    if clip.isFinished():
        removeElementFromSet(state["visited"],name)
        if not glob.sound.isPlaying("jake_FINAL/sound/victory2.aiff"):
                glob.sound.play("jake_FINAL/sound/victory2.aiff")
        return "youwin"
    else: return "-1"
def graph_Bdies_1(state,clip):
    return Bdies_generic(state,clip,"Bdies_1")
def graph_Bdies_2(state,clip):
    return Bdies_generic(state,clip,"Bdies_2")
def graph_Bdies_3(state,clip):
    return Bdies_generic(state,clip,"Bdies_3")
def graph_Bdies_4(state,clip):
    return Bdies_generic(state,clip,"Bdies_4")
def graph_Bdies_5(state,clip):
    return Bdies_generic(state,clip,"Bdies_5")

def graph_youwin(state,clip):
    if clip.isFinished():
        return "youlose"
    else: return "-1"

def YT_generic(state,clip,name):
    blink(state,clip)
    if clip.isFinished():
        removeElementFromSet(state["visited"],name) 
        state["turn"] = "Y"
        saveMemory(state,"wait")
        return "wait"
    else: return "-1"
def graph_YT_1(state,clip):
    return YT_generic(state,clip,"YT_1")
def graph_YT_2(state,clip):
    return YT_generic(state,clip,"YT_2")
def graph_YT_3(state,clip):
    return YT_generic(state,clip,"YT_3")

def graph_truecontinue(state,clip):
    if state["press"] and clip.getTime() > 1:
        state["press"] = False
        s,r =  loadMemory(state)
        if "MEMORY" in state:
            s["MEMORY"] = copy.deepcopy(state["MEMORY"])
        #TODO state is not being assigned properly, need to do value by value
        #print state
        print "LOADED, checking state", s["visited"] == state["visited"]
        state.clear()
        state.update(s)
        
        #print state
        return r
    if clip.isFinished(): return "gameover"
    else: return "-1"
def graph_gameover(state,clip):
    if clip.isFinished():
        if not glob.sound.isPlaying("jake_FINAL/sound/victory2.aiff"):
                glob.sound.play("jake_FINAL/sound/victory2.aiff")
        return "youwin"
    else: return "-1"
def graph_continue(state,clip):
    #TODO play some music and shit
    if clip.isFinished():
        if(stupid(state,clip)): return "bandaid"
        #return "truecontinue"
        return "gameover"
    else: return "-1"
def graph_youlose(state,clip):
    if clip.isFinished():
        state["RESET"] = 0
        return "-1"
    else: return "-1"
    
def SH1_generic(state,clip,name):
    blink(state,clip)
    if state["lose"]:
        return youlose(state,clip)
    if clip.isFinished():
        removeElementFromSet(state["visited"],name) 
        return "waitlean"
    else: return "-1"
def graph_SH1_1(state,clip):
    return SH1_generic(state,clip,"SH1_1")
def graph_SH1_2(state,clip):
    return SH1_generic(state,clip,"SH1_2")
def graph_SH1_3(state,clip):
    return SH1_generic(state,clip,"SH1_3")

def SH2_generic(state,clip,name):
    blink(state,clip)
    if state["lose"]:
        return youlose(state,clip)
    if clip.isFinished():
        removeElementFromSet(state["visited"],name) 
        return "waitlean"
    else: return "-1"
def graph_SH2_1(state,clip):
    return SH2_generic(state,clip,"SH2_1")
def graph_SH2_2(state,clip):
    return SH2_generic(state,clip,"SH2_2")
def graph_SH2_3(state,clip):
    return SH2_generic(state,clip,"SH2_3")

def graph_SH2(state,clip):
    blink(state,clip)
    if clip.isFinished(): return "BshootsY"
    else: return "-1"
def graph_SH3(state,clip):
    blink(state,clip)
    if clip.isFinished():
        state["shots_fired"] += 1
        if random.randint(0,5) <= state["shots_fired"]-1:
            return youlose(state,clip) 
        else:
            glob.sound.play("jake_FINAL/sound/click.aiff")
            return "FY"
    else: return "-1"
    
    
def lucky_generic(state,clip,name):
    blink(state,clip)
    if clip.isFinished():
        removeElementFromSet(state["visited"],name) 
        return "wait" #random.choice(getSubset(state["visited"],["Btakesgun",]))[1]
    else: return "-1"
def graph_lucky_1(state,clip):
    return lucky_generic(state,clip,"lucky_1")
def graph_lucky_2(state,clip):
    return lucky_generic(state,clip,"lucky_2")
def graph_lucky_3(state,clip):
    return lucky_generic(state,clip,"lucky_3")
#stupid clips
def graph_bandaid(state,clip):
    if clip.isFinished():
        #return "truecontinue"
        return "gameover"
    else: return -1
def graph_funny_lucky(state,clip):
    blink(state,clip)
    if clip.isFinished():
        return random.choice(getSubset(state["visited"],["Btakesgun",]))[1]
    else: return -1
def graph_crowdgoeswild(state,clip):
    blink(state,clip)
    if clip.isFinished():
        return "wait"
    else: return -1
    
def graph_sideways_1(state,clip):
    blink(state,clip)
    if clip.isFinished():
        return "wait"
    else: return -1
def graph_sideways_2(state,clip):
    blink(state,clip)
    if clip.isFinished():
        return "wait"
    else: return -1
def graph_blowgun(state,clip):
    blink(state,clip)
    if clip.isFinished():
        state["turn"] = "Y"
        return "wait"
    else: return -1
    
#player functions
def graph_player_blank(state,clip):
    if state["turn"] == "Y":
        if state["player_shoot_state"] == 0 and state["press"]:
            state["player_shoot_state"] = 1
            return "player_handin"
        
    return "-1"
def graph_player_blank_patch(state,clip):
    #if state["lose"]:
        #add additional checks here
        #return "-1"
    if clip.getTime() > 0.5:
        state["eyes_open"] = False
    if not state["press"] and not state["player_shoot_state"] == 3:
        state["player_shoot_state"] = 0
        return "player_handout" 
    elif state["press"] and time.time() - state["time_pressed"] > 4.5:
        state["press"] = False
        state["turn"] = "B"
        if random.randint(0,5) <= state["shots_fired"]-1:
            state["lose"] = True
            return "player_blank"
        else:
            state["FH_state"] = 0
            #state["first_hesitate"]
            state["first_shot"] = False
            state["player_shoot_state"] = 3
            glob.sound.play("jake_FINAL/sound/click.aiff")
            return "-1"
    elif state["player_shoot_state"] == 3 and clip.getTime() > 4.5:
        state["player_shoot_state"] = 2
        return "player_handout"
    return "-1"
def graph_player_handin(state,clip):
    if clip.isFinished(): return "player_blank_patch"
    else: return "-1"
def graph_player_handout(state,clip):
    state["eyes_open"] = True
    if clip.isFinished(): return "player_blank"
    else: return "-1"
    
    
#eye functions
def graph_eyes_closing(state,clip):
    if state["lose"] and clip.getTime()>5:
        state["eyes_open"] = True
        return "eyes_blank"
    if clip.isFinished() and state["eyes_open"]:
        return "eyes_openning" 
    else: return "-1"
def graph_eyes_openning(state,clip): 
    if clip.isFinished(): return "eyes_blank"
    else: return "-1"
def graph_eyes_blank(state,clip):
    #TODO fix bug here where you can not shoot when blinking
    if state["blinking"] and state["player_shoot_state"] == 0:
        return "eyes_blink"
    if not state["eyes_open"]:
        return "eyes_closing"
    return "-1"
def graph_eyes_blink(state,clip):
    if clip.isFinished():
        state["blinking"] = False 
        return "eyes_blank"
    else: return "-1"
    
def graph_fade_blank(state,clip):
    if clip.isFinished():
        if state["fade"]:
            return "fade_fadeout"
        return "-1"
    else: return "-1"
def graph_fade_black(state,clip):
    if clip.isFinished():
        if not state["fade"]:
            return "fade_fadein"
        else: return "-1"
    else: return "-1"
def graph_fade_fadein(state,clip):
    if clip.isFinished():
        return "fade_blank"
    else: return "-1"
def graph_fade_fadeout(state,clip):
    if clip.isFinished():
        return "fade_black"
    else: return "-1"
