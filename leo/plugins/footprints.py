#@+leo-ver=4-thin
#@+node:pap.20041020001240:@thin footprints.py
""" 
A plugin to leave footprints! This colours the Leo nodes so that the ones you
have visited most and most recently will stand out.
"""

# By Paul Paterson. Most of the drawing code and idea from the cleo plugin by Mark Ng.

__version__ = "0.3" 
__plugin_name__ = "Footprints" 

#@<< version history >>
#@+node:pap.20041020001240.1:<< version history >>
#@@killcolor
#@+at 
# 
# 0.1 Paul Paterson: Initial version.
# 0.2 EKR:
#     - Added init method.
#     - Not safe for unit testing because of lock.acquire.
#       That is, not installed properly by unit tests.
# 
# 0.3 EKR:
#     - Declared click_registry and coloured_nodes global in init.
#@-at
#@nonl
#@-node:pap.20041020001240.1:<< version history >>
#@nl
#@<< imports >>
#@+node:pap.20041020001240.2:<< imports >>
import leo.core.leoGlobals as g 
import leo.core.leoPlugins as leoPlugins 

import leo.plugins.tkGui as tkGui
leoTkinterTree = tkGui.leoTkinterTree

try: 
    import Tkinter as Tk 
except ImportError: 
    Tk = g.cantImport("Tkinter")

if g.isPython3:
    import configparser as ConfigParser
else:
    import ConfigParser

import threading 
import time 

#@-node:pap.20041020001240.2:<< imports >>
#@nl
#@<< todo >>
#@+node:pap.20041020001240.3:<< todo >>
""" 

Todo list: 

- pretty much everything 

""" 
#@-node:pap.20041020001240.3:<< todo >>
#@nl

#@+others
#@+node:ekr.20050310105438:init
def init ():

    ok = Tk and not g.app.unitTesting # Not safe for unit testing because of lock.

    global click_registry, coloured_nodes

    if ok:
        if g.app.gui is None:
            g.app.createTkGui(__file__)

        ok = g.app.gui.guiName() == "tkinter"

        if ok:
            # Internal controls 
            click_registry = {} 
            coloured_nodes = set() 
            applyConfiguration(getConfiguration()) 
            # 
            leoPlugins.registerHandler("start2", installDrawMethod) 
            leoPlugins.registerHandler("headclick1", storeHeadlineClick) 
            g.plugin_signon(__name__)

    return ok
#@-node:ekr.20050310105438:init
#@+node:pap.20041020001240.5:Error Classes
pass 
#@nonl
#@-node:pap.20041020001240.5:Error Classes
#@+node:pap.20041020001240.55:Implementation
#@+node:pap.20041020012447:getConfiguration
def getConfiguration(): 
    """Return the config object""" 
    fileName = g.os_path_join(g.app.loadDir,"../","plugins","footprints.ini") 
    config = ConfigParser.ConfigParser() 
    config.read(fileName) 
    return config 
#@-node:pap.20041020012447:getConfiguration
#@+node:pap.20041020012723:applyConfiguration
def applyConfiguration(config): 
    """Called when the user selects Properties from the menu""" 
    global REFRESH, COLD_FG, HOT_FG, HITS_TO_HOT 
    REFRESH = config.getint("Main", "RefreshInterval") 
    COLD_FG = config.get("Main", "ColdColour") 
    HOT_FG = config.get("Main", "HotColour") 
    HITS_TO_HOT = config.getint("Main", "HitsToHeatUp") 
#@-node:pap.20041020012723:applyConfiguration
#@+node:pap.20041020001800:installDrawMethod
registered = False 

def installDrawMethod(tags, kw): 
    global registered 
    if registered: 
        return 

    g.funcToMethod(doFootprint, 
        leoTkinterTree, 
        "setUnselectedLabelState") 

    registered = True 

    updater = threading.Thread(target=updateNodes) 
    updater.setDaemon(True) 
    updater.start() 

    global lock 
    lock = threading.Lock() 
#@-node:pap.20041020001800:installDrawMethod
#@+node:pap.20041020001841:doFootprint
def doFootprint(self, p):  
    """Do the colouring"""
    c = self.c
    if p and c.edit_widget(p): 
        config = g.app.config 

        #fg = config.getWindowPref("headline_text_unselected_foreground_color") 
        #bg = config.getWindowPref("headline_text_unselected_background_color") 
        fg = COLD_FG      
        bg = "white" 

        if click_registry.get(p.v, 0) >= HITS_TO_HOT: 
            fg, bg = HOT_FG, "white" 
            coloured_nodes.add(p) 

        try: 
            c.edit_widget(p).configure( 
                state="disabled",highlightthickness=0, fg=fg, bg=bg) 
        except: 
         g.es_exception()
#@-node:pap.20041020001841:doFootprint
#@+node:pap.20041020002741:storeHeadlineClick
def storeHeadlineClick(tag, keywords): 
    """A node headline was clicked""" 
    lock.acquire() 
    try: 
        node = keywords['p'] 
        click_registry[node.v] = max(click_registry.get(node.v, 0), 0)+1  
        #g.pr("adding to ", node, click_registry[node.v] )
    finally: 
        lock.release() 
#@nonl
#@-node:pap.20041020002741:storeHeadlineClick
#@+node:pap.20041020004243:updateNodes
def updateNodes(): 
    """Update the colour of nodes""" 
    config = g.app.config 
    #fg = config.getWindowPref("headline_text_unselected_foreground_color") 
    #bg = config.getWindowPref("headline_text_unselected_background_color") 
    fg, bg = COLD_FG, "white" 

    while 1: 
        time.sleep(REFRESH) # Sleep for indicated number of seconds.
        # 
        lock.acquire() 
        # 
        # Look for nodes about to expire 
        try: 
            expired = set(); done = set() 
            #g.pr(coloured_nodes )
            for node in coloured_nodes: 
                if node.v not in done: 
                    done.add(node.v) 
                    click_registry[node.v] = click_registry[node.v]-1 
                    #g.pr("decreasing", node.v, click_registry[node.v] )
                    if click_registry[node.v] <= 0: 
                        #g.pr("removing", node.v )
                        expired.add(node) 
                        if c.edit_widget(node): 
                            c.edit_widget(node).configure( 
                                state="disabled",highlightthickness=0, fg=fg, bg=bg) 
            # 
            # Remove the expired nodes - cannot do that in the loop above 
            # because we are iterating over the set 
            for node in expired: 
                coloured_nodes.remove(node) 
            # 
        finally: 
            lock.release() 
#@-node:pap.20041020004243:updateNodes
#@-node:pap.20041020001240.55:Implementation
#@-others
#@-node:pap.20041020001240:@thin footprints.py
#@-leo
