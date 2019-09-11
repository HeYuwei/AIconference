# from util import get_cite_num
from util import *


def get_abstract(item):
    # if 'abstract' in item.keys() and len(item['abstract']) > 10:
    #     print('ab ' + str(item['abstract']))
    #     return item['abstract']
    # url = 'http://proceedings.mlr.press/v48/guha16.html'
    # url = 'https://www.ijcai.org/proceedings/2019/419'
    # url = 'https://cn.bing.com/academic/profile?id=e06403eeba6f4f2caa57d899348883fc&encoded=0&v=paper_preview&mkt=zh-cn'
    title = 'abnormal event discovery in user generated photos.'
    # title = item['title']
    root = 'https://cn.bing.com'
    words = title.split()
    url = root + '/academic/search?q='
    for word in words:
        url += word + '+'
    url = url[:-1]
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    url = root + soup.select('li.aca_algo > h2 a')[0]['href']
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    text_list = get_children_text(soup)
    title_list = get_children_title(soup)
    text_list.extend(title_list)
    for text in text_list:
        # print(text)
        if text == '摘　　要':
            # for ch in soup.descendants:
            #     try:
            #         print('title ' +  ch['title'])
            #         # ch['title']
            #     except:
            #         pass

            print('read finished')
            ab = get_longest_text(text_list)
            print(ab)
            item['abstract'] = ab
            return ab


    # # url = item['url']
    # url = 'https://www.aaai.org/ocs/index.php/AAAI/AAAI16/paper/view/12280'
    # r = requests.get(url)
    # soup = BeautifulSoup(r.content, 'html.parser')
    # text_list = get_children_text(soup)
    # ab = get_longest_text(text_list)
    # # item['abstract'] = ab
    # return ab


# c = get_cite_num('placing objects in gesture space: toward incremental interpretation of multimodal spatial descriptions.')
# c = get_basic_info()

# get_abstract(None)

s = refresh_sentence('345fsfd l;cvo23 c;kf *(^# lsdo3')
print(s)
# c = get_cite_num('Heterogeneous Transfer Learning for Image Classification')
# c = 1