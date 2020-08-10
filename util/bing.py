from . import *
import semanticscholar as sch

def get_abstract(item,soup):
    # url = 'http://proceedings.mlr.press/v48/guha16.html'
    # url = 'https://www.ijcai.org/proceedings/2019/419'
    # url = 'https://cn.bing.com/academic/profile?id=e06403eeba6f4f2caa57d899348883fc&encoded=0&v=paper_preview&mkt=zh-cn'

    # if conf == 'arxiv':
    #     p_url = item['url']
    #     soup = get_soup(p_url)
    #     ab = soup.find(class_='abstract mathjax').text
    #     ab = ab.lstrip()
    #     ab = ab.replace('Abstract:','')
    #     ab = ab.replace('\n','')
    #     ab = break_line(ab)
    #     item['abstract'] = ab
    #     return ab

    root = 'https://cn.bing.com'
    included = True
    try:
        url = root + soup.select('li.aca_algo > h2 a')[0]['href']
    except:
        included = False

    if included:

        soup = get_soup(url)
        if soup is not None:

            text_list = get_children_text(soup)
            title_list = get_children_title(soup)
            text_list.extend(title_list)
            for ind,text in enumerate(text_list):
                # print(text)
                if text == '摘　　要':
                    ab = get_longest_text(text_list)
                    # ab = text_list[ind + 2]
                    # print('the ab')
                    # print(ab)
                    ab = ab.lstrip()
                    ab = break_line(ab)
                    item['abstract'] = ab
                    return ab

    url = item['url']
    soup = get_soup(url)
    if soup is None:
        print('The internet is in trouble!')
        item['abstract'] = ''
        return ''

    text_list = get_children_text(soup)
    try:
        ab = get_longest_text(text_list)
    except:
        ab = 'Not Accessible'
    ab = ab.lstrip()
    ab = break_line(ab)
    item['abstract'] = ab
    return ab

def get_cite_num(p_item,soup):
    cite_num = -1
    items = soup.find_all(class_='aca_algo')[:5]

    for i,item in enumerate(items):
        # tmp_title = item.select('h2 > a')[0].text
        # minDis = minDistance(p_item['title'], tmp_title.lower())
        # if minDis < 70:
        #     the_item = item
        #     break
        # else:
        #     if i == len(items) - 1:
        #         the_item = items[0]
        #
        # try:
        #     if i == len(items) - 1:
        #         item = items[0]
        try:
            item = items[i]
            cite_num = 0
            item = item.find(class_='caption_venue')
            for j in range(len(item.contents)):
                value = str(item.contents[j])
                if value.startswith('被'):
                    cite_num = int(item.select('a')[1].text)
                    break
        except:
            continue
        break

    p_item['cite_num'] = cite_num
    return cite_num


def supply_basic_info(item,conf,refresh_info):
    # abstract
    has_abstract = False
    has_cite = False

    if not refresh_info and 'abstract' in item.keys() and len(item['abstract']) > 10:
        has_abstract = True

    if not refresh_info and 'cite_num' in item.keys() and item['cite_num'] >= 0:
        has_cite = True

    if not(has_abstract and has_cite):
        if 'doi' in item.keys() and item['doi'] is not None:
            get_semantic_info(item)
        else:
            get_bing_info(item, has_abstract, has_cite)

    return item


    # print(item['abstract'])


def get_bing_info(item, has_abstract, has_cite):
    title = item['title']
    root = 'https://cn.bing.com'
    url = root + '/academic/search?q='
    url_title = parse.quote(title)
    url += url_title
    soup = get_soup(url)

    if not has_abstract:
        get_abstract(item,soup)

    if not has_cite:
        get_cite_num(item,soup)

def get_semantic_info(item):
    doi = item['doi']
    paper = sch.paper(doi)
    if paper is None:
        return item

    citation = len(paper['citations'])
    abstract = break_line(paper['abstract'])
    item['cite_num'] = citation
    item['abstract'] = abstract

    return item
