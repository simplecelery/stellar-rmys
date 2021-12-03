import time
import StellarPlayer
import math
import json
import os
import sys
import requests
from shutil import copyfile

class rmysplugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self,player:StellarPlayer.IStellarPlayer):
        super().__init__(player)
        self.configjson = ''
        self.medias = []
        self.pageindex = 0
        self.pagenumbers = 0
        self.cur_page = ''
        self.max_page = ''
        self.pg = ''
        self.wd = ''
        self.source = []
        self.allmovidesdata = {}
        self.mediasize = 18
    
    def start(self):
        super().start()
        self.configjson = 'source.json'
        jsonpath = self.player.dataDirectory + '\\source.json'
        if os.path.exists(jsonpath) == False:
            localpath = os.path.split(os.path.realpath(__file__))[0] + '\\source.json'
            print(localpath)
            if os.path.exists(localpath):
                try:
                    copyfile(localpath,jsonpath)
                except IOError as e:
                    print("Unable to copy file. %s" % e)
                except:
                    print("Unexpected error:", sys.exc_info())
        down_url = "https://cdn.jsdelivr.net/gh/nomoodhalashao/my-movie@main/source.json"
        try:
            r = requests.get(down_url,timeout = 5,verify=False) 
            result = r.status_code
            if result == 200:
                with open(self.configjson,'wb') as f:
                    f.write(r.content)
        except:
            print('get remote source.json error')
        self.loadSource()
    
    def loadSource(self):
        self.loadSourceFile(self.configjson)
        displaynum = min(len(self.source),self.mediasize)
        self.medias = []
        for i in range(displaynum):
            self.medias.append(self.source[i])
        self.pageindex = 1
        self.pagenumbers = len(self.source) // self.mediasize
        if self.pagenumbers * self.mediasize < len(self.source):
            self.pagenumbers = self.pagenumbers + 1
        self.cur_page = '第' + str(self.pageindex) + '页'
        self.max_page = '共' + str(self.pagenumbers) + '页'   

      
    def loadSourceFile(self,file):
        file = open(file, "rb")
        fileJson = json.loads(file.read())
        print(len(fileJson))
        for item in fileJson:
            newitem = {'title':item['name'],'fullname':item['fullname'],'picture':item['pic_url'],'info':item['detail'],'url':item['magnet']}
            self.source.append(newitem)
        file.close()    
    
    def show(self):
        controls = self.makeLayout()
        self.doModal('main',800,680,'',controls)        
    
    def makeLayout(self):
        mediagrid_layout = [
            [
                {
                    'group': [
                        {'type':'image','name':'picture', '@click':'on_grid_click'},
                        {'type':'link','name':'title','textColor':'#ff7f00','fontSize':13,'height':0.15,'hAlign':'center','@click':'on_grid_click'}
                    ],
                    'dir':'vertical'
                }
            ]
        ]
        controls = [
            {'type':'space','height':5},
            {'type':'grid','name':'mediagrid','itemlayout':mediagrid_layout,'value':self.medias,'separator':True,'itemheight':200,'itemwidth':130},
            {'group':
                [
                    {'type':'space'},
                    {'group':
                        [
                            {'type':'label','name':'cur_page',':value':'cur_page'},
                            {'type':'link','name':'首页','fontSize':13,'@click':'onClickFirstPage'},
                            {'type':'link','name':'上一页','fontSize':13,'@click':'onClickFormerPage'},
                            {'type':'link','name':'下一页','fontSize':13,'@click':'onClickNextPage'},
                            {'type':'link','name':'末页','fontSize':13,'@click':'onClickLastPage'},
                            {'type':'label','name':'max_page',':value':'max_page'},
                        ]
                        ,'width':0.7
                    },
                    {'type':'space'}
                ]
                ,'height':30
            },
            {'type':'space','height':5}
        ]
        return controls
            
        
    def on_grid_click(self, page, listControl, item, itemControl):
        mediainfo = self.medias[item]
        self.createMediaFrame(mediainfo)
        
    def createMediaFrame(self,mediainfo):
        medianame = mediainfo['title']
        self.allmovidesdata[medianame] = mediainfo['url']
        controls = [
            {'type':'space','height':10},
            {'group':[
                    {'type':'image','name':'mediapicture', 'value':mediainfo['picture'],'width':0.4},
                    {'type':'space','width':10},
                    {'group':[
                            {'type':'label','name':'medianame','textColor':'#ff7f00','fontSize':15,'value':mediainfo['fullname'],'height':40},
                            {'type':'space','height':10},
                            {'type':'label','name':'info','textColor':'#005555','value':mediainfo['info'],'height':250,'vAlign':'top'},
                            {'type':'space','height':5},
                        {'group':[
                    {'type':'space','width':20},
                    {'type':'link','name':'下载','fontSize':16,'width':150,'vAlign':'center','@click':'onDownClick'}, 
                    {'type':'space','width':15},
                    {'type':'link','name':'播放','fontSize':16,'width':150,'vAlign':'center','@click':'onPlayClick'}
                    ]
                    }
                        ],
                        'dir':'vertical'
                    },
                    {'type':'space','width':10}
                ],
                'width':1.0
            },
            {'type':'space','height':10}
        ]
        result,control = self.doModal(mediainfo['title'],680,400,'',controls)

    def onDownClick(self, pageId, control, *args):
        url = self.allmovidesdata[pageId]
        self.player.download(url)
    
    def onPlayClick(self, pageId, control, *args):
        url = self.allmovidesdata[pageId]
        self.player.play(url)

    def loadPageData(self):
        maxnum = len(self.source)
        if (self.pageindex - 1) * self.mediasize > maxnum:
            return
        self.medias = []
        startnum = (self.pageindex - 1) * self.mediasize
        endnum = self.pageindex * self.mediasize
        endnum = min(maxnum,endnum)
        print(startnum)
        print(endnum)
        for i in range(startnum,endnum):
            self.medias.append(self.source[i])
        self.cur_page = '第' + str(self.pageindex) + '页'
        self.player.updateControlValue('main','mediagrid',self.medias)
       
    def onClickFirstPage(self, *args):
        self.pageindex = 1
        self.loading()
        self.loadPageData()
        self.loading(True)
        
    def onClickFormerPage(self, *args):
        if self.pageindex == 1:
            return
        self.pageindex = self.pageindex - 1;
        self.loading()
        self.loadPageData()
        self.loading(True)
    
    def onClickNextPage(self, *args):
        if self.pageindex >= self.pagenumbers:
            return
        self.pageindex = self.pageindex + 1
        self.loading()
        self.loadPageData()
        self.loading(True)
        
    def onClickLastPage(self, *args):
        self.pageindex = self.pagenumbers
        self.loading()
        self.loadPageData()
        self.loading(True)
        
    def loading(self, stopLoading = False):
        if hasattr(self.player,'loadingAnimation'):
            self.player.loadingAnimation('main', stop=stopLoading)
        
def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = rmysplugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()