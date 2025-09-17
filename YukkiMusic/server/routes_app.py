from aiohttp import web_app
import aiohttp as request_n
from aiohttp.http_exceptions import BadStatusLine
import asyncio
import jinja2
import urllib.parse
import argparse
from aiohttp import web, ClientSession, ClientTimeout
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import aiohttp_jinja2
from typing import Any, Dict
import json
from YukkiMusic.platforms.Youtube_scrap import search_player_data_with_post_api
# try:
#     loop = asyncio.get_running_loop()
# except RuntimeError:  # no running event loop
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
# session = ClientSession()

#from YukkiMusic.alive import web_server

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
    return web.Response(text="Hello from app v1!")

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
            assert resp.status == 200
            text = await resp.text()

            try:
                data = json.loads(text)
                return data   # Suggestions list
            except json.JSONDecodeError:
                print("Failed to parse JSON:", text)
                return []


async def download_file_in_chunks(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }
    print(url)
    
    async with ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    while True:
                        chunk = await response.content.read(1024)  # Read 1024 bytes at a time
                        if not chunk:
                            break
                        yield chunk  # Yield each chunk as it's read
                else:
                    print(f"Failed to download file. Status code: {response.status}")
        except asyncio.TimeoutError:
            print("Request timed out.")
        except Exception as e:
            print(f"Error occurred: {e}")



async def download_video(request: web.Request):
    range_header = request.headers.get("Range", 0) 
    
    query = request.query.get('id','')
    
    strem_list = await search_player_data_with_post_api(query)
    loop = asyncio.get_running_loop()
    def get_video_url():
           
        for stream in strem_list:
            if stream["mimeType"].find('video/mp4'):
                video_url=stream['url']
                #file_size = stream['contentLength']
                file_type=stream["mimeType"]
                break
            else:
                continue
        return video_url,file_type
    '''def get_audio_url():

        
        for stream in strem_list:
            if stream["mimeType"].find('audio/mp4'):
                audio_url=stream['url']
                break
            else:
                continue
        return audio_url'''
    video_url,file_type= await loop.run_in_executor(
                None, get_video_url
            )
    '''audio_url = await loop.run_in_executor(
                None, get_audio_url
            )'''
    '''if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        #until_bytes = int(until_bytes) if until_bytes else int(file_size) - 1
    else:
        #stop_value = int(request.http_range.stop) if request.http_range.stop else file_size
        from_bytes = request.http_range.start or 0
        #until_bytes = int(file_size) - 1
    #print(video_url,file_size,query,strem_list)'''
    return web.Response(
      status=206 if range_header else 200,
      body=download_file_in_chunks(video_url),
      headers={
          "Content-Type": file_type,
          #"Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
          #"Content-Length": str(file_size),
          "Content-Disposition": f'inline; filename="video_{query}.mp4"',
          "Accept-Ranges": "bytes",
      },
  )

async def download_audio(request: web.Request):
    range_header = request.headers.get("Range", 0)
    query = request.query.get('id','')
   
    strem_list = await search_player_data_with_post_api(query)
    loop = asyncio.get_running_loop()
    '''def get_video_url():
            
        for stream in strem_list:
            if stream["mimeType"].find('video/mp4'):
                video_url=stream['url']
                break
            else:
                continue
        return video_url'''
    def get_audio_url():

        
        for stream in strem_list:
            if stream["mimeType"].find('audio/mp4'):
                audio_url=stream['url']
                #file_size = stream['contentLength']
                file_type=stream["mimeType"]
                break
            else:
                continue
        return audio_url,file_type
    '''video_url = await loop.run_in_executor(
                None, get_video_url
            )'''
    audio_url,file_type = await loop.run_in_executor(
                None, get_audio_url
            )
    
    '''if range_header:
        #from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        #until_bytes = int(until_bytes) if until_bytes else int(file_size) - 1
    else:
        #stop_value = int(request.http_range.stop) if request.http_range.stop else file_size
        from_bytes = request.http_range.start or 0
        #until_bytes =int(file_size) - 1
'''
    return web.Response(
      status=206 if range_header else 200,
      body=download_file_in_chunks(audio_url),
      headers={
          "Content-Type": file_type,
          #"Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
          #"Content-Length": str(file_size),
          "Content-Disposition": f'inline; filename="audio_{query}.mp4"',
          "Accept-Ranges": "bytes",
      },
  )
    


#@sub_app.get("/up", allow_head=True)
@aiohttp_jinja2.template("index.html")    
async def Index_page(request: web.Request) -> Dict[str, Any]:
    return {'page':'main'}

@aiohttp_jinja2.template("index.html")    
async def Home_Component(request: web.Request) -> str:
    # html_content = f"""
    # <section id="home">
    #     <h1>Home Page{str("hello")}</h1>
    #     <p>Content for the Home page goes here.</p>
    # </section>
    # """
    # return web.Response(text=html_content, content_type='text/html')
    return {'page':'home','data':''}
@aiohttp_jinja2.template("index.html")    
async def Subscribe_Component(request: web.Request) :
    return {'page':'subscribed'}

@aiohttp_jinja2.template("index.html")    
async def Search_Component(request: web.Request):
    query = request.query.get('q', '').lower()
    pagetoken = request.query.get('pageToken', '') if request.query.get('pageToken', '') else ''

    DEVELOPER_KEY = 'AIzaSyBzPhFUOwRp-WarINiS34I7LJyBDx6mPTQ'
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
    
    if request.query.get('type', '')=='json':
        
        return web.json_response({"page":"search","data": videos,"nextPageToken":search_response.get('nextPageToken','')})
    else:
        return{'page':'search','data':videos,'nextPageToken':search_response.get('nextPageToken','')}

    
@aiohttp_jinja2.template("index.html")   
async def Playlist_Component(request: web.Request) :
    pass
@aiohttp_jinja2.template("index.html")   
async def Function_Component(request: web.Request) :
    return {'page':'functions'}

sub_app = web.Application()
aiohttp_jinja2.setup(sub_app,loader=jinja2.FileSystemLoader('YukkiMusic/server/templates/Home/pages/'))
#env=aiohttp_jinja2.get_env(sub_app)
#env.globals.update(url_find=url_find)
#sub_app['static_root_url']='../static/'
sub_app.router.add_static('/static/', path='YukkiMusic/server/templates/Home/static/', name='static')
sub_app.router.add_get('/', handle_v2)
sub_app.router.add_get('/main', Index_page,name='main')
sub_app.router.add_get('/home', Home_Component, name='home')
sub_app.router.add_get('/subscribed', Subscribe_Component, name='subscribed')
sub_app.router.add_get('/searchquery',searchquery,name='searchquery')
sub_app.router.add_get('/search', Search_Component, name='search')
sub_app.router.add_get('/playlist', Playlist_Component)
sub_app.router.add_get('/functions', Function_Component, name='functions')
sub_app.router.add_get('/nextPage', nextPage, name='nextPage')
sub_app.router.add_get('/dlv', download_video, name='dlv')
sub_app.router.add_get('/dla', download_audio, name='dla')


'''
sub_app.add_routes([
    web.get('/main', Index_page,name='main'),
    web.get('/home', Home_Component, name='home'),
    web.get('/subscribed', Subscribe_Component, name='subscribed'),
    web.get('/functions', Function_Component, name='functions')])'''
