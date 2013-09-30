NAME = 'The Onion'
BASE_URL = 'http://www.theonion.com'
MAIN_PAGE = 'http://www.theonion.com/video'

RE_DURATION = Regex("\((?P<mins>[0-9]+):(?P<secs>[0-9]+)\)")

####################################################################################################
def Start():

  Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')

  ObjectContainer.title1 = NAME
  ObjectContainer.view_group = 'List'
  HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
@handler('/video/theonion', NAME)
def MainMenu():

  oc = ObjectContainer()
  html = HTML.ElementFromURL(MAIN_PAGE)

  for show in html.xpath('//img[@title="The Onion Video"]/../../..//li//a'):
    title = show.xpath('./text()')[0]
    url = show.xpath('./@href')[0]

    if title not in ('Promos'):
      oc.add(DirectoryObject(
        key = Callback(Episodes, show_url=url, show_title=title),
        title = title
      ))

  return oc

####################################################################################################
@route('/video/theonion/episodes', page=int)
def Episodes(show_url, show_title, page=1):

  oc = ObjectContainer(title2=show_title)
  html = HTML.ElementFromURL('%s%s?page=%d' % (BASE_URL, show_url, page))

  for episode in html.xpath('//div[@class="episodes"]/article'):
    url = episode.xpath('.//h1/a/@href')[0]

    if not url.startswith('http://'):
      url = '%s%s' % (BASE_URL, url)

    title = episode.xpath('.//h1/a/text()')[0]
    thumb = episode.xpath('.//img/@data-src')[0].replace('/260.jpg', '/640.jpg').split('?')[0]
    duration = episode.xpath('.//span[@class="duration"]/text()')[0]

    oc.add(VideoClipObject(
      url = url,
      title = title,
      thumb = Resource.ContentsOfURLWithFallback(thumb),
      duration = Datetime.MillisecondsFromString(duration)
    ))

  if len(html.xpath('//li[@class="next"]')) > 0:
    oc.add(NextPageObject(
      key = Callback(Episodes, show_url=show_url, show_title=show_title, page=page+1),
      title = 'Next Page ...'
    ))

  return oc
