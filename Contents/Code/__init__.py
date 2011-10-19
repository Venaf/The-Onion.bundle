import re

TO_PLUGIN_PREFIX   = "/video/theonion"
TO_BASE_URL        = "http://www.theonion.com"

CACHE_INTERVAL     = 1000 # HTTP cache interval in seconds
MAX_RESULTS        = "100"

MAIN_PAGE          = "http://www.theonion.com/content/video"
TO_AJAX            = "http://www.theonion.com/ajax/onn_playlist/%s/%s" #% show name %pagenum

NAME = "The Onion"
ART = "art-default.jpg"
ICON = "icon-default.jpg"
SEARCH = "icon-search.png"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(TO_PLUGIN_PREFIX, MainMenu, NAME, ICON, ART)
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")  
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

  ObjectContainer.art = R(ART)
  ObjectContainer.title1 = NAME
  ObjectContainer.view_group = "List"

  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  VideoClipObject.thumb = R(ICON)
  VideoClipObject.art = R(ART)

####################################################################################################
def MainMenu():
  oc = ObjectContainer()
  oc.add(DirectoryObject(key = Callback(Shows), title = "Shows"))

  page = HTML.ElementFromURL(MAIN_PAGE, cacheTime = CACHE_INTERVAL)
  categories = page.xpath('//div[@id="side_recirc"]/div')

  for category in categories:
    id = category.get("rel")
    title = category.xpath("a")[0].text
    oc.add(DirectoryObject(key = Callback(PopulateFromHTML, show_id = id, show_title = title), title = title))

  oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.theonion", title = "Search...", prompt = "Search for clips", thumb = R(SEARCH)))
  return oc

####################################################################################################
def Shows():
  oc = ObjectContainer(title2 = "Shows")

  page = HTML.ElementFromURL(MAIN_PAGE, cacheTime = CACHE_INTERVAL)
  shows = page.xpath('//ul[@id="categories"]//li')

  for show in shows:
    if show.get("class") != "label":
      title = show.xpath("a")[0].text_content()
      id = show.get("rel")
      oc.add(DirectoryObject(key = Callback(PopulateFromHTML, show_id = id, show_title = title), title = title))

  return oc

####################################################################################################
def PopulateFromHTML(show_id, show_title = '', replace_parent = False,  page = 1):
  oc = ObjectContainer(view_group = "InfoList", title2 = str(show_title) + ' - Page ' + str(page), replace_parent = replace_parent)

  if page > 1 :
    oc.add(DirectoryObject(key = Callback(PopulateFromHTML, show_id = id, show_title = title, page = page - 1, replace_parent = True), title = 'Previous Page ...'))

  page = HTML.ElementFromURL(TO_AJAX % (show_id, page))

  for element in page.xpath("//li"):
    url = element.xpath('.//a')[0].get('href')

    if url.startswith('/video/') == False:
      continue
    else:
      url = TO_BASE_URL + url

    title = element.xpath('.//p[@class="title"]//text()')[0]
    summary = element.xpath('.//p[@class="teaser"]')[0].text
    thumb = element.xpath('.//img')[0].get('src')

    info = element.xpath('.//p[@class="info"]/text()')[0].strip()
    info_dict = re.match("\((?P<mins>[0-9]+):(?P<secs>[0-9]+)\)", info).groupdict()
    mins = int(info_dict['mins'])
    secs = int(info_dict['secs'])
    duration = ((mins * 60) + secs) * 1000

    oc.add(VideoClipObject(
      url = url,
      title = title,
      summary = summary,
      thumb = Function(GetThumb,url=thumb),
      duration = duration))

  try: 
    resp = HTTP.Request(TO_AJAX % (show_id, int(page + 1))).content
    oc.add(DirectoryObject(key = Callback(PopulateFromHTML, show_id = id, show_title = title, page = page + 1, replace_parent = replace_parent), title = 'Next Page ...'))
    dir.Append(Function(DirectoryItem(populateFromHTML, title = 'Next Page ...'),show_id = show_id, show_title = show_title, page = page+1, replaceParent = True))
  except:
    pass

  return oc

####################################################################################################
def GetThumb(url):
  try:
    full_url = url[:url.find('_jpg_')] + '.jpg'
    data = HTTP.Request(full_url, cacheTime = CACHE_1WEEK).content
    return DataObject(data, 'image/jpeg')
  except:
    try:
      data = HTTP.Request(url, cacheTime = CACHE_1WEEK).content
      return DataObject(data, 'image/jpeg')
    except:
      return Redirect(R(ICON))