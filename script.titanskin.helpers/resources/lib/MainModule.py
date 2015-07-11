import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import shutil
import xbmcaddon
import xbmcvfs
import os, sys
import time
import urllib
import xml.etree.ElementTree as etree
from xml.dom.minidom import parse
import json
import random

import Utils as utils

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom
import xml.etree.cElementTree as ET

doDebugLog = False

win = xbmcgui.Window( 10000 )
addon = xbmcaddon.Addon(id='script.titanskin.helpers')
addondir = xbmc.translatePath(addon.getAddonInfo('profile'))

__language__ = xbmc.getLocalizedString
__cwd__ = addon.getAddonInfo('path')


def sendClick(controlId):
    win = xbmcgui.Window( 10000 )
    time.sleep(0.5)
    xbmc.executebuiltin('SendClick('+ controlId +')')

def defaultSettings():
    # skins default settings for artist slideshow
    if xbmc.getCondVisibility("System.HasAddon(script.artistslideshow)"):
        __settings__ = xbmcaddon.Addon(id='script.artistslideshow')
        __settings__.setSetting('transparent', "true")
      
def musicSearch():
    xbmc.executebuiltin( "ActivateWindow(MusicLibrary)" )
    xbmc.executebuiltin( "SendClick(8)" )
    
        
def showInfoPanel():
    tryCount = 0
    secondsToDisplay = "4"
    secondsToDisplay = xbmc.getInfoLabel("Skin.String(ShowInfoAtPlaybackStart)")
    if win.getProperty("VideoScreensaverRunning") != "true":
        while tryCount !=50 and not xbmc.getCondVisibility("Window.IsActive(fullscreeninfo)"):
            time.sleep(0.1)
            if not xbmc.getCondVisibility("Window.IsActive(fullscreeninfo)") and xbmc.getCondVisibility("Player.HasVideo"):
                xbmc.executebuiltin('Action(info)')
            tryCount += 1
        
        # close info again
        time.sleep(int(secondsToDisplay))
        if xbmc.getCondVisibility("Window.IsActive(fullscreeninfo)"):
            xbmc.executebuiltin('Action(info)')

def addShortcutWorkAround():
    xbmc.executebuiltin('SendClick(301)')
    
    count = 0
    #wait for the empy item is focused
    while (count != 60 and xbmc.getCondVisibility("Window.IsActive(script-skinshortcuts.xml)")):
        if not xbmc.getCondVisibility("StringCompare(Container(211).ListItem.Property(path), noop)"):
            xbmc.sleep(100)
            count += 1
        else:
            break
        
    if xbmc.getCondVisibility("StringCompare(Container(211).ListItem.Property(path), noop) + Window.IsActive(script-skinshortcuts.xml)"):
        xbmc.executebuiltin('SendClick(401)')
    
                 
def getFavourites():
    try:
        xbmcplugin.setContent(int(sys.argv[1]), 'files')
        favoritesCount = 0
        fav_file = xbmc.translatePath( 'special://profile/favourites.xml' ).decode("utf-8")
        if xbmcvfs.exists( fav_file ):
            doc = parse( fav_file )
            listing = doc.documentElement.getElementsByTagName( 'favourite' )
            
            for count, favourite in enumerate(listing):
                label = ""
                image = "special://skin/extras/hometiles/favourites.png"
                for (name, value) in favourite.attributes.items():
                    if name == "name":
                        label = value
                    if name == "thumb":
                        image = value
                path = favourite.childNodes [ 0 ].nodeValue
                
                path="plugin://script.titanskin.helpers?LAUNCHAPP&&&" + path
                li = xbmcgui.ListItem(label, path=path)
                li.setThumbnailImage(image)
                li.setProperty('IsPlayable', 'false')
                
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=path, listitem=li, isFolder=False)
    except Exception as e: 
        print "exception ?"
        print e
        pass        
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def selectOverlayTexture():
    overlaysList = []
    overlaysList.append("Custom Overlay Image")
    dirs, files = xbmcvfs.listdir("special://skin/extras/bgoverlays/")
    for file in files:
        if file.endswith(".png"):
            label = file.replace(".png","")
            overlaysList.append(label)
    
    overlaysList.append("None")
    
    dialog = xbmcgui.Dialog()
    ret = dialog.select(xbmc.getLocalizedString(31470), overlaysList)
    if ret == 0:
        dialog = xbmcgui.Dialog()
        custom_texture = dialog.browse( 2 , xbmc.getLocalizedString(31457), 'files')
        if custom_texture:
            xbmc.executebuiltin("Skin.SetString(ColorThemeTexture,Custom)")
            xbmc.executebuiltin("Skin.SetString(CustomColorThemeTexture,%s)" % custom_texture)
    else:
        xbmc.executebuiltin("Skin.SetString(ColorThemeTexture,%s)" % overlaysList[ret])
        xbmc.executebuiltin("Skin.Reset(CustomColorThemeTexture)")

def selectBusyTexture():
    
    xbmc.executebuiltin( "ActivateWindow(busydialog)" )
    import Dialogs as dialogs
    spinnersList = []
    
    currentSpinnerTexture = xbmc.getInfoLabel("Skin.String(SpinnerTexture)")
    
    listitem = xbmcgui.ListItem(label="None")
    listitem.setProperty("icon","None")
    spinnersList.append(listitem)
    
    listitem = xbmcgui.ListItem(label="Custom single image (gif)")
    listitem.setProperty("icon","special://skin/extras/icons/animated-gif-icon.png")
    spinnersList.append(listitem)
    
    listitem = xbmcgui.ListItem(label="Custom multi image (path)")
    listitem.setProperty("icon","special://skin/extras/icons/animated-spinner-folder-icon.png")
    spinnersList.append(listitem)

    dirs, files = xbmcvfs.listdir("special://skin/extras/busy_spinners/")
    
    for dir in dirs:
        listitem = xbmcgui.ListItem(label=dir)
        listitem.setProperty("icon","special://skin/extras/busy_spinners/" + dir)
        spinnersList.append(listitem)
    
    for file in files:
        if file.endswith(".gif"):
            label = file.replace(".gif","")
            listitem = xbmcgui.ListItem(label=label)
            listitem.setProperty("icon","special://skin/extras/busy_spinners/" + file)
            spinnersList.append(listitem)

    w = dialogs.DialogSelectBig( "DialogSelect.xml", __cwd__, listing=spinnersList, windowtitle="select trailer",multiselect=False )
    
    count = 0
    for li in spinnersList:
        if li.getLabel() == currentSpinnerTexture:
            w.autoFocusId = count
        count += 1
         
    xbmc.executebuiltin( "Dialog.Close(busydialog)" )
    w.doModal()
    selectedItem = w.result
    del w
    
    if selectedItem == -1:
        return
    
    if selectedItem == 1:
        dialog = xbmcgui.Dialog()
        custom_texture = dialog.browse( 2 , xbmc.getLocalizedString(31504), 'files', mask='.gif')
        if custom_texture:
            xbmc.executebuiltin("Skin.SetString(SpinnerTexture,%s)" %spinnersList[selectedItem].getLabel())
            xbmc.executebuiltin("Skin.SetString(SpinnerTexturePath,%s)" % custom_texture)
    elif selectedItem == 2:
        dialog = xbmcgui.Dialog()
        custom_texture = dialog.browse( 0 , xbmc.getLocalizedString(31504), 'files')
        if custom_texture:
            xbmc.executebuiltin("Skin.SetString(SpinnerTexture,%s)" %spinnersList[selectedItem].getLabel())
            xbmc.executebuiltin("Skin.SetString(SpinnerTexturePath,%s)" % custom_texture)
    else:
        xbmc.executebuiltin("Skin.SetString(SpinnerTexture,%s)" %spinnersList[selectedItem].getLabel())
        xbmc.executebuiltin("Skin.SetString(SpinnerTexturePath,%s)" % spinnersList[selectedItem].getProperty("icon"))
                
def enableViews():
    import Dialogs as dialogs
    
    allViews = []   
    views_file = xbmc.translatePath( 'special://skin/extras/views.xml' ).decode("utf-8")
    if xbmcvfs.exists( views_file ):
        doc = parse( views_file )
        listing = doc.documentElement.getElementsByTagName( 'view' )
        for count, view in enumerate(listing):
            id = view.attributes[ 'value' ].nodeValue
            label = xbmc.getLocalizedString(int(view.attributes[ 'languageid' ].nodeValue)) + " (" + str(id) + ")"
            type = view.attributes[ 'type' ].nodeValue
            listitem = xbmcgui.ListItem(label=label)
            listitem.setProperty("id",id)
            if not xbmc.getCondVisibility("Skin.HasSetting(View.Disabled.%s)" %id):
                listitem.select(selected=True)
            allViews.append(listitem)
    
    w = dialogs.DialogSelectSmall( "DialogSelect.xml", __cwd__, listing=allViews, windowtitle=xbmc.getLocalizedString(31487),multiselect=True )
    w.doModal()
    
    selectedItems = w.result
    if selectedItems != -1:
        itemcount = len(allViews) -1
        while (itemcount != -1):
            viewid = allViews[itemcount].getProperty("id")
            if itemcount in selectedItems:
                #view is enabled
                xbmc.executebuiltin("Skin.Reset(View.Disabled.%s)" %viewid)
            else:
                #view is disabled
                xbmc.executebuiltin("Skin.SetBool(View.Disabled.%s)" %viewid)
            itemcount -= 1    
    del w        

def setForcedView(contenttype):
    currentView = xbmc.getInfoLabel("Skin.String(ForcedViews.%s)" %contenttype)
    selectedItem = selectView(contenttype, currentView, True, True)
    
    if selectedItem != -1 and selectedItem != None:
        xbmc.executebuiltin("Skin.SetString(ForcedViews.%s,%s)" %(contenttype, selectedItem))
    
def setView():
    #sets the selected viewmode for the container
    import Dialogs as dialogs
    
    #get current content type
    contenttype="other"
    if xbmc.getCondVisibility("Container.Content(episodes)"):
        contenttype = "episodes"
    elif xbmc.getCondVisibility("Container.Content(movies) + !substring(Container.FolderPath,setid=)"):
        contenttype = "movies"  
    elif xbmc.getCondVisibility("[Container.Content(sets) | StringCompare(Container.Folderpath,videodb://movies/sets/)] + !substring(Container.FolderPath,setid=)"):
        contenttype = "sets"
    elif xbmc.getCondVisibility("substring(Container.FolderPath,setid=)"):
        contenttype = "setmovies" 
    elif xbmc.getCondVisibility("Container.Content(tvshows)"):
        contenttype = "tvshows"
    elif xbmc.getCondVisibility("Container.Content(seasons)"):
        contenttype = "seasons"
    elif xbmc.getCondVisibility("Container.Content(musicvideos)"):
        contenttype = "musicvideos"
    elif xbmc.getCondVisibility("Container.Content(artists)"):
        contenttype = "artists"
    elif xbmc.getCondVisibility("Container.Content(songs)"):
        contenttype = "songs"
    elif xbmc.getCondVisibility("Container.Content(albums)"):
        contenttype = "albums"
    elif xbmc.getCondVisibility("Container.Content(songs)"):
        contenttype = "songs"
    elif xbmc.getCondVisibility("Window.IsActive(tvchannels) | Window.IsActive(radiochannels)"):
        contenttype = "tvchannels"
    elif xbmc.getCondVisibility("Window.IsActive(tvrecordings) | Window.IsActive(radiorecordings)"):
        contenttype = "tvrecordings"
    elif xbmc.getCondVisibility("Window.IsActive(programs) | Window.IsActive(addonbrowser)"):
        contenttype = "programs"
    elif xbmc.getCondVisibility("Window.IsActive(pictures)"):
        contenttype = "pictures"
    
    currentView = xbmc.getInfoLabel("Container.Viewmode")
    selectedItem = selectView(contenttype, currentView)
    currentForcedView = xbmc.getInfoLabel("Skin.String(ForcedViews.%s)" %contenttype)
    
    #also store forced view    
    if currentForcedView != "None":
        xbmc.executebuiltin("Skin.SetString(ForcedViews.%s,%s)" %(contenttype, selectedItem))
    
    #set view
    if selectedItem != -1 and selectedItem != None:
        xbmc.executebuiltin("Container.SetViewMode(%s)" %selectedItem)
    
def searchTrailer(title):
    xbmc.executebuiltin( "ActivateWindow(busydialog)" )
    import Dialogs as dialogs
    libPath = "plugin://plugin.video.youtube/kodion/search/query/?q=%s Trailer" %title
    media_array = None
    allTrailers = []
    media_array = utils.getJSON('Files.GetDirectory','{ "properties": ["title","art","plot"], "directory": "' + libPath + '", "media": "files", "limits": {"end":25} }')
    if(media_array != None and media_array.has_key('files')):
        for media in media_array['files']:
            
            if not media["filetype"] == "directory":
                label = media["label"]
                label2 = media["plot"]
                image = None
                if media.has_key('art'):
                    if media['art'].has_key('thumb'):
                        image = (media['art']['thumb'])
                        
                path = media["file"]
                listitem = xbmcgui.ListItem(label=label, label2=label2, iconImage=image)
                listitem.setProperty("path",path)
                listitem.setProperty("icon",image)
                allTrailers.append(listitem)

    w = dialogs.DialogSelectBig( "DialogSelect.xml", __cwd__, listing=allTrailers, windowtitle="select trailer",multiselect=False )
    xbmc.executebuiltin( "Dialog.Close(busydialog)" )
    w.doModal()
    selectedItem = w.result
    del w
    if selectedItem != -1:
        path = allTrailers[selectedItem].getProperty("path")
        xbmc.executebuiltin("PlayMedia(%s)" %path)
            
def getNextEpisodes():
    limit = 25
    count = 0
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    # First we get a list of all the in-progress TV shows
    json_query_string = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": { "sort": { "order": "descending", "method": "lastplayed" }, "filter": {"and": [{"operator":"true", "field":"inprogress", "value":""}]}, "properties": [ "title", "studio", "mpaa", "file", "art" ] }, "id": "1"}')

    json_result = json.loads(json_query_string)
    # If we found any, find the oldest unwatched show for each one.
    if json_result.has_key('result') and json_result['result'].has_key('tvshows'):
        for item in json_result['result']['tvshows']:
            json_query2 = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": { "tvshowid": %d, "sort": {"method":"episode"}, "filter": {"and": [ {"field": "playcount", "operator": "lessthan", "value":"1"}, {"field": "season", "operator": "greaterthan", "value": "0"} ]}, "properties": [ "title", "playcount", "season", "episode", "showtitle", "plot", "file", "rating", "resume", "tvshowid", "art", "streamdetails", "firstaired", "runtime", "writer", "cast", "dateadded", "lastplayed" ], "limits":{"end":1}}, "id": "1"}' %item['tvshowid'])
            if json_query2:
                json_query2 = json.loads(json_query2)
                if json_query2.has_key('result') and json_query2['result'].has_key('episodes'):
                    
                    for item in json_query2['result']['episodes']:
                        liz = utils.createListItem(item)
                        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=item['file'], listitem=liz)
                        count +=1
                        if count == limit:
                            break
                            
    if count < limit:
        # Fill the list with first episodes of unwatched tv shows
        json_query_string = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": { "sort": { "order": "ascending", "method": "dateadded" }, "filter": {"and": [{"operator":"false", "field":"inprogress", "value":""}]}, "properties": [ "title", "studio", "mpaa", "file", "art" ] }, "id": "1"}')
        json_result = json.loads(json_query_string)
        if json_result.has_key('result') and json_result['result'].has_key('tvshows'):
            for item in json_result['result']['tvshows']:
                json_query2 = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": { "tvshowid": %d, "sort": {"method":"episode"}, "filter": {"and": [ {"field": "playcount", "operator": "lessthan", "value":"1"}, {"field": "season", "operator": "greaterthan", "value": "0"} ]}, "properties": [ "title", "playcount", "season", "episode", "showtitle", "plot", "file", "rating", "resume", "tvshowid", "art", "streamdetails", "firstaired", "runtime", "writer", "cast", "dateadded", "lastplayed" ], "limits":{"end":1}}, "id": "1"}' %item['tvshowid'])
                if json_query2:
                    json_query2 = json.loads(json_query2)
                    if json_query2.has_key('result') and json_query2['result'].has_key('episodes'):
                        
                        for item in json_query2['result']['episodes']:
                            liz = utils.createListItem(item)
                            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=item['file'], listitem=liz)
                            count +=1
                            if count == limit:
                                break
        
        
    
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))

def getRecommendedMovies():
    limit = 25
    count = 0
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    # First we get a list of all the in-progress Movies
    json_query_string = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "sort": { "order": "descending", "method": "lastplayed" }, "filter": {"and": [{"operator":"true", "field":"inprogress", "value":""}]}, "properties": [ "title", "playcount", "plot", "file", "rating", "resume", "art", "streamdetails", "year", "runtime", "writer", "cast", "dateadded", "lastplayed" ] }, "id": "1"}')
    json_result = json.loads(json_query_string)
    # If we found any, find the oldest unwatched show for each one.
    if json_result.has_key('result') and json_result['result'].has_key('movies'):
        for item in json_result['result']['movies']:
            liz = utils.createListItem(item)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=item['file'], listitem=liz)
            count +=1
            if count == limit:
                break
    
    # Fill the list with random items with a score higher then 7
    json_query_string = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "sort": { "order": "descending", "method": "random" }, "filter": {"and": [{"operator":"is", "field":"playcount", "value":"0"},{"operator":"greaterthan", "field":"rating", "value":"7"}]}, "properties": [ "title", "playcount", "plot", "file", "rating", "resume", "art", "streamdetails", "year", "runtime", "writer", "cast", "dateadded", "lastplayed" ] }, "id": "1"}')
    json_result = json.loads(json_query_string)
    # If we found any, find the oldest unwatched show for each one.
    if json_result.has_key('result') and json_result['result'].has_key('movies'):
        for item in json_result['result']['movies']:
            liz = utils.createListItem(item)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=item['file'], listitem=liz)
            count +=1
            if count == limit:
                break
    
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
    
def getRecommendedMedia(ondeckOnly=True):
    limit = 25
    count = 0
    allItems = []
    allTitles = list()
    xbmcplugin.setContent(int(sys.argv[1]), 'files')
    # Get a list of all the in-progress Movies
    json_query_string = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "sort": { "order": "descending", "method": "lastplayed" }, "filter": {"and": [{"operator":"true", "field":"inprogress", "value":""}]}, "properties": [ "title", "playcount", "plot", "file", "rating", "resume", "art", "streamdetails", "year", "mpaa", "runtime", "writer", "cast", "dateadded", "lastplayed", "tagline" ] }, "id": "1"}')
    json_result = json.loads(json_query_string)
    if json_result.has_key('result') and json_result['result'].has_key('movies'):
        for item in json_result['result']['movies']:
            lastplayed = item["lastplayed"]
            if not item["title"] in allTitles:
                allItems.append((lastplayed,item))
                allTitles.append(item["title"])
    
    # Get a list of all the in-progress MusicVideos
    json_query_string = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMusicVideos", "params": { "sort": { "order": "descending", "method": "lastplayed" }, "limits": { "start" : 0, "end": 25 }, "properties": [ "title", "playcount", "plot", "file", "resume", "art", "streamdetails", "year", "runtime", "dateadded", "lastplayed" ] }, "id": "1"}')
    json_result = json.loads(json_query_string)
    if json_result.has_key('result') and json_result['result'].has_key('musicvideos'):
        for item in json_result['result']['musicvideos']:
            lastplayed = item["lastplayed"]
            if not item["title"] in allTitles and item["resume"]["position"] != 0:
                allItems.append((lastplayed,item))
                allTitles.append(item["title"])
    
    # Get a list of all the in-progress music songs
    json_query_string = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetRecentlyPlayedSongs", "params": { "sort": { "order": "descending", "method": "lastplayed" }, "limits": { "start" : 0, "end": 5 }, "properties": [ "artist", "title", "rating", "fanart", "thumbnail", "duration", "playcount", "comment", "file", "album", "lastplayed" ] }, "id": "1"}')
    json_result = json.loads(json_query_string)
    if json_result.has_key('result') and json_result['result'].has_key('songs'):
        for item in json_result['result']['songs']:
            lastplayed = item["lastplayed"]
            if not item["title"] in allTitles and lastplayed and item["thumbnail"]:
                allItems.append((lastplayed,item))
                allTitles.append(item["title"])
    
    # NextUp episodes
    json_query_string = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": { "sort": { "order": "descending", "method": "lastplayed" }, "filter": {"and": [{"operator":"true", "field":"inprogress", "value":""}]}, "properties": [ "title", "studio", "mpaa", "file", "art" ] }, "id": "1"}')
    json_result = json.loads(json_query_string)
    if json_result.has_key('result') and json_result['result'].has_key('tvshows'):
        for item in json_result['result']['tvshows']:
            json_query2 = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": { "tvshowid": %d, "sort": {"method":"episode"}, "filter": {"and": [ {"field": "playcount", "operator": "lessthan", "value":"1"}, {"field": "season", "operator": "greaterthan", "value": "0"} ]}, "properties": [ "title", "playcount", "season", "episode", "showtitle", "plot", "file", "rating", "mpaa", "resume", "tvshowid", "art", "streamdetails", "firstaired", "runtime", "writer", "cast", "dateadded", "lastplayed" ], "limits":{"end":1}}, "id": "1"}' %item['tvshowid'])
            if json_query2:
                json_query2 = json.loads(json_query2)
                if json_query2.has_key('result') and json_query2['result'].has_key('episodes'):
                    
                    for item in json_query2['result']['episodes']:
                        lastplayed = item["lastplayed"]
                        if not item["title"] in allTitles:
                            allItems.append((lastplayed,item))
                            allTitles.append(item["title"])            
    
    
    #sort the list with in progress items by lastplayed date   
    from operator import itemgetter
    allItems = sorted(allItems,key=itemgetter(0),reverse=True)
    
    if not ondeckOnly:
        # Random movies with a score higher then 7
        json_query_string = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "sort": { "order": "descending", "method": "random" }, "filter": {"and": [{"operator":"is", "field":"playcount", "value":"0"},{"operator":"greaterthan", "field":"rating", "value":"7"}]}, "properties": [ "title", "playcount", "plot", "file", "rating", "resume", "art", "streamdetails", "year", "runtime", "writer", "cast", "dateadded", "lastplayed" ] }, "id": "1"}')
        json_result = json.loads(json_query_string)
        # If we found any, find the oldest unwatched show for each one.
        if json_result.has_key('result') and json_result['result'].has_key('movies'):
            for item in json_result['result']['movies']:
                lastplayed = item["lastplayed"]
                if not item["title"] in set(allTitles):
                    allItems.append((lastplayed,item))
                    allTitles.append(item["title"])

    #build that listing
    for item in allItems:
        liz = utils.createListItem(item[1])
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=item[1]['file'], listitem=liz)
        count +=1
        if count == limit:
            break       
    
   
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))    
    
def selectView(contenttype="other", currentView=None, displayNone=False, displayViewId=False):
    import Dialogs as dialogs
    currentViewSelectId = None

    allViews = []
    if displayNone:
        listitem = xbmcgui.ListItem(label="None")
        listitem.setProperty("id","None")
        allViews.append(listitem)
        
    views_file = xbmc.translatePath( 'special://skin/extras/views.xml' ).decode("utf-8")
    if xbmcvfs.exists( views_file ):
        doc = parse( views_file )
        listing = doc.documentElement.getElementsByTagName( 'view' )
        itemcount = 0
        for count, view in enumerate(listing):
            label = __language__(int(view.attributes[ 'languageid' ].nodeValue))
            id = view.attributes[ 'value' ].nodeValue
            if displayViewId:
                label = label + " (" + str(id) + ")"
            type = view.attributes[ 'type' ].nodeValue
            if label.lower() == currentView.lower() or id == currentView:
                currentViewSelectId = itemcount
                if displayNone == True:
                    currentViewSelectId += 1
            if (type == "all" or contenttype in type) and not xbmc.getCondVisibility("Skin.HasSetting(View.Disabled.%s)" %id):
                image = "special://skin/extras/viewthumbs/%s.jpg" %id
                listitem = xbmcgui.ListItem(label=label, iconImage=image)
                listitem.setProperty("id",id)
                listitem.setProperty("icon",image)
                allViews.append(listitem)
                itemcount +=1
    w = dialogs.DialogSelectBig( "DialogSelect.xml", __cwd__, listing=allViews, windowtitle="select view",multiselect=False )
    w.autoFocusId = currentViewSelectId
    w.doModal()
    selectedItem = w.result
    del w
    if selectedItem != -1:
        id = allViews[selectedItem].getProperty("id")
        return id
    