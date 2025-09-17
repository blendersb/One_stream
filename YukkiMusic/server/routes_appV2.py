from aiohttp import web
import aiohttp as request_n
from aiohttp.http_exceptions import BadStatusLine
import asyncio
import jinja2
import urllib.parse
import argparse
from aiohttp import web, ClientSession
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from YukkiMusic.platforms.Youtube_scrap import tranding_videos,search_videos,search_videos_with_post_api,search_scroll_videos_with_post_api,trending_with_post_api
import aiohttp_jinja2
from typing import Any, Dict
import json

#from YukkiMusic.alive import web_server
# try:
#     loop = asyncio.get_running_loop()
# except RuntimeError:  # no running event loop
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
# session = ClientSession()
parser = argparse.ArgumentParser()
parser.add_argument('--q', help='Search term', default='Google')
parser.add_argument('--max-results', help='Max results', default=25)
args = parser.parse_args()

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
def url_find(route_name, *args, **kwargs):
    # Check if route belongs to sub-application
    if route_name.startswith('subapp_'):
        route_name = route_name[len('subapp_'):]
        return str(sub_app.router[route_name])
    # Otherwise, it belongs to the main application
    return str('/')

async def handle_v2(request):
    return web.Response(text="Hello from app v2!")

async def nextPage(request):
    query = request.query.get('q', '').lower()
    DEVELOPER_KEY = 'AIzaSyAJB2yzah87l58QCNUFrYOrzu_5I7RFQZY'
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'


    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

    # Call the search.list method to retrieve results matching the specified
    # query term.
    if request.query.get('pageToken', ''):
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            pageToken=request.query.get('pageToken', ''),
            maxResults=args.max_results
        ).execute()
    else:
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=args.max_results
        ).execute()
    
    #search_response=""
    videos = []
    channels = []
    playlists = []

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    #search_result['snippet']['title'],
    #search_result['id']['videoId']
    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            videos.append(search_result)
        elif search_result['id']['kind'] == 'youtube#channel':
            channels.append('%s (%s)' % (search_result['snippet']['title'],
                                    search_result['id']['channelId']))
        elif search_result['id']['kind'] == 'youtube#playlist':
            playlists.append('%s (%s)' % (search_result['snippet']['title'],
                                        search_result['id']['playlistId']))
        #print(videos)
    data=str({'page':'search','data':videos,'nextPageToken':search_response.get('nextPageToken','')})


    return web.Response(text=data)
    
async def searchquery(request):
    query = request.query.get('q', '').lower()
    url = f"http://suggestqueries.google.com/complete/search?client=firefox&q={query}"

    async with ClientSession() as session:
        async with session.get(url) as resp:
            # If remote returns non-200, return empty list or forward error
            if resp.status != 200:
                return web.json_response([], status=resp.status)

            text = await resp.text()

            try:
                data = json.loads(text)
                suggestions = data if isinstance(data[1], list) and len(data) > 1 else []
                # Return an actual aiohttp Response (JSON)
                return web.json_response(suggestions)
            except json.JSONDecodeError:
                # sometimes the remote may respond with invalid JSON; return empty array
                return web.json_response([], status=200)
            '''assert resp.status == 200
            text = await resp.text()

            try:
                data = json.loads(text)
                return data[1]   # Suggestions list
            except json.JSONDecodeError:
                print("Failed to parse JSON:", text)
                return []'''
    
    '''async with request_n.request('GET',
            f'https://cors-handlers.vercel.app/api/?url=http%3A%2F%2Fsuggestqueries.google.com%2Fcomplete%2Fsearch%3Fclient%3Dfirefox%26ds%3Dyt%26q={query}') as resp:
        assert resp.status == 200
        #print(await resp.text())
    #async with session.get(f'https://cors-handlers.vercel.app/api/?url=http%3A%2F%2Fsuggestqueries.google.com%2Fcomplete%2Fsearch%3Fclient%3Dfirefox%26ds%3Dyt%26q={query}') as resp:
        data=await resp.text()
    #print(data)
    #return web.Response(text=query)
    return web.Response(text=data)
    #async with session.get(f'https://cors-handlers.vercel.app/api/?url=http%3A%2F%2Fsuggestqueries.google.com%2Fcomplete%2Fsearch%3Fclient%3Dfirefox%26ds%3Dyt%26q={query}') as resp:
            #data=await resp.text()
    #print(data)
    #return web.Response(text=data)
    #return query'''

#@sub_app.get("/up", allow_head=True)
@aiohttp_jinja2.template("index.html")    
async def Index_page(request: web.Request) -> Dict[str, Any]:

    return {'page':'main'}

@aiohttp_jinja2.template("index.html")    
async def Home_Component(request: web.Request):
    
    query = 'Now' if request.query.get('q', '') == '' else request.query.get('q', '')
        
       
    videos = await trending_with_post_api(query)
    # html_content = f"""
    # <section id="home">
    #     <h1>Home Page{str("hello")}</h1>
    #     <p>Content for the Home page goes here.</p>
    # </section>
    # """
    # return web.Response(text=html_content, content_type='text/html')
    return{'page':'home','data':videos}
    
@aiohttp_jinja2.template("index.html")    
async def Subscribe_Component(request: web.Request) :
    return {'page':'subscribed'}

@aiohttp_jinja2.template("index.html")    
async def Search_Component(request: web.Request):
    query = request.query.get('q', '')
    
    #videos = await search_videos(query)
    videos, nextPageToken = await search_videos_with_post_api(query)
    if request.query.get('type', '')=='json':
        
        return web.json_response({"page":"search","data": videos,'nextPageToken':nextPageToken})
    else:
        return{'page':'search','data':videos,'nextPageToken':nextPageToken}
    
@aiohttp_jinja2.template("index.html")    
async def Scroll_Component(request: web.Request):
    query = request.query.get('q', '')
    
    #videos = await search_videos(query)
    videos, nextPageToken = await search_scroll_videos_with_post_api(query)
    if request.query.get('type', '')=='json':
        
        return web.json_response({"page":"search","data": videos,"nextPageToken":nextPageToken})
    else:
        return{'page':'search','data':videos,'nextPageToken':nextPageToken}

    
@aiohttp_jinja2.template("index.html")   
async def Playlist_Component(request: web.Request) :
    pass
@aiohttp_jinja2.template("index.html")   
async def Function_Component(request: web.Request) :
    return {'page':'functions'}

sub_appV2 = web.Application()
aiohttp_jinja2.setup(sub_appV2,loader=jinja2.FileSystemLoader('YukkiMusic/server/templates/HomeV2/pages/'))
#env=aiohttp_jinja2.get_env(sub_app)
#env.globals.update(url_find=url_find)
#sub_app['static_root_url']='../static/'
sub_appV2.router.add_static('/static/', path='YukkiMusic/server/templates/HomeV2/static/', name='static')
sub_appV2.router.add_get('/', handle_v2)
sub_appV2.router.add_get('/main', Index_page,name='main')
sub_appV2.router.add_get('/home', Home_Component, name='home')
sub_appV2.router.add_get('/subscribed', Subscribe_Component, name='subscribed')
sub_appV2.router.add_get('/searchquery',searchquery,name='searchquery')
sub_appV2.router.add_get('/search', Search_Component, name='search')
sub_appV2.router.add_get('/playlist', Playlist_Component)
sub_appV2.router.add_get('/functions', Function_Component, name='functions')
#sub_appV2.router.add_get('/nextPage', nextPage, name='nextPage')
sub_appV2.router.add_get('/scroll', Scroll_Component, name='scroll')


'''
sub_app.add_routes([
    web.get('/main', Index_page,name='main'),
    web.get('/home', Home_Component, name='home'),
    web.get('/subscribed', Subscribe_Component, name='subscribed'),
    web.get('/functions', Function_Component, name='functions')])'''
