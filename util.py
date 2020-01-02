import matplotlib.pyplot as plt
import importlib
import json
import os
from bs4 import BeautifulSoup
from urllib import parse
import requests
import re
import csv
import time

def gen_save_name(opt,func_name):
    save_name = func_name + '_'
    if 'arxiv' in opt.conf_list:
        save_name += 'arxiv_'

    for key in opt.keywords.keys():
        if len(opt.keywords[key]) > 0:
            save_name += key + '['
            for w in opt.keywords[key]:
                save_name += w + ','
            save_name = save_name[:-1] + ']_'

    save_name += 'time('
    for t in opt.time_sec:
        save_name += t + ','
    save_name = save_name[:-1] + ')'
    return save_name

def assert_info(opt):
    if len(opt.conf_list) > 1 and 'arxiv' in opt.conf_list:
        assert False, 'arxiv must be acount solely!'
    recorded_confs =  list(opt.conf_info.keys())
    # print(str(recorded_confs))
    for conf in opt.conf_list:
        if conf not in recorded_confs:
            assert False, 'The info of ' + conf + ' must be recorded first!'

    for t in opt.time_sec:
        assert len(t) == 4 or len(t) == 6, 'The time unit should be year or mouth'

def ex_funtion(opt):
    keywords = {}
    keywords['m'] = opt.key_words_m
    keywords['c'] = opt.key_words_c
    keywords['r'] = opt.key_words_r
    opt.keywords = keywords

    model_filename = "apps." + opt.function
    modellib = importlib.import_module(model_filename)
    func = getattr(modellib,opt.function)
    func(opt)

    # target_model_name = model_name.replace('_', '') + 'model'
    # for name, cls in modellib.__dict__.items():
    #     if name.lower() == target_model_name.lower() \
    #        and issubclass(cls, BaseModel):
    #         model = cls

def init_conf_info():
    conf_info = {}
    with open('conf_info.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            conf_info[row['name']] = row

    return conf_info

def revise_conf_info(conf_info,conf,key,value):
    conf_info[conf][key] = value
    return conf_info

def addTips(content,keywords):
    words = []
    words.extend(keywords['m'])
    words.extend(keywords['c'])

    for word in words:
        word = word.lstrip()
        word = word.rstrip()
        if len(word) > 0:
            content = content.replace(word,'$$'+word+'$$')
    return content

def get_titles(conf ,conf_info, c_time,with_a = False):
    if conf == 'arxiv':
        return get_arxiv_info(c_time = c_time,with_a = with_a)

    if not os.path.exists('papers/' + conf):
        os.mkdir('papers/' + conf)


    if (conf_info[conf]['hold_time'] == 'single' and int(c_time) % 2 == 0) or (conf_info[conf]['hold_time'] == 'double' and int(c_time) % 2 == 1):
        print(conf + ' is not hold in ' + c_time)
        return []

    suffix = ''
    if with_a:
        suffix += '_a'

    fname = 'papers/' + conf + '/' + c_time + suffix + '.json'

    if os.path.exists(fname):
        with open(fname,'r',encoding='utf-8') as f:
            data = json.load(f)
            return data.values()
    else:
        if conf_info[conf]['type'] == 'conf':
            if conf in ['cvpr','iccv']:
                url = 'http://openaccess.thecvf.com/' + conf.upper() + c_time + '.py'
                soup = get_soup(url)
                items = soup.find_all(class_ = 'ptitle')
                titles = []
                for item in items:
                    item = item.select('a')[0]
                    title = item.text.lower()
                    url = 'http://openaccess.thecvf.com/' + item['href']
                    titles.append((title, url))


            else:
                titles = one_page_titles(conf, conf_info, c_time, volume='')

                if len(titles) == 0:
                    # print('There may be several volumes')

                    start_v = 1
                    while True:
                        volume = '-' + str(start_v)
                        tmp_titles = one_page_titles(conf,conf_info, c_time, volume=volume)
                        if len(tmp_titles) == 0:
                            break
                        titles.extend(tmp_titles)
                        start_v += 1
        else:
            url = 'https://dblp.org/db/journals/' + conf + '/'
            v_ind = 2019 - int(c_time)
            soup = get_soup(url)
            v_info = soup.select('div#main > ul > li > a')[v_ind].text
            v_ind = re.split(r' |:', v_info)[1]
            titles = one_page_titles(conf,conf_info, v_ind, volume='')

        if len(titles) == 0:
            print(conf + c_time + ' does not exisit')
            return titles
            # return []
        else:
            mkdir('papers')
            content = {}
            for i,item in enumerate(titles):
                content[str(i)] = {}
                content[str(i)]['title'] = item[0]
                content[str(i)]['url'] = item[1]
                content[str(i)]['abstract'] = ''
                content[str(i)]['cite_num'] = -1
                content[str(i)]['conf'] = conf
                content[str(i)]['time'] = c_time

            with open(fname,'w',encoding='utf8') as f:
                json.dump(content,f)

            return content.values()

def one_page_titles(conf,conf_info,c_time,volume = ''):

    url = 'https://dblp.org/db/' + conf_info[conf]['type'] + '/' + conf_info[conf]['parent'] + '/' + conf + c_time + volume + '.html'
    # print(url)
    soup = get_soup(url)

    if conf_info[conf]['type'] == 'conf':
        items = soup.find_all(class_='entry inproceedings')
    else:
        items = soup.find_all(class_='entry article')

    titles = []
    for item in items:
        title = item.find(class_ = 'title').text.lower()
        url = item.find(class_ = 'ee').find('a').get('href')
        titles.append((title,url))
    return titles

def get_arxiv_info(c_time,fields=['math.OC','cs.LG','stat.ML','cs.CV'], with_a = False):
    suffix = ''
    if with_a:
        suffix = '_a'

    times = time.strftime('%Y %m %d', time.localtime(time.time())).split()
    sys_time = times[0][2:] + times[1]
    if int(sys_time) < int(c_time):
        print(c_time + ' is not reached.')
        return []

    f_name = 'papers/arxiv/' + c_time + suffix + '.json'

    if os.path.exists(f_name):
        with open(f_name,'r') as f:
            data = json.load(f)
            return data.values()
    else:
        paper_content = {}
        p_count = 0

        p_ids = []
        root_url = 'https://arxiv.org'

        mkdir('papers/arxiv/')

        for field in fields:
            url = root_url + '/list/' + field + '/' + c_time
            # print(url)
            soup = get_soup(url)

            page = soup.find(id='dlpage')
            all_parts = page.select('small')[1]
            all_url = all_parts.select('a')[2]['href']
            url = root_url + all_url

            soup = get_soup(url)

            page = soup.find(id='dlpage')

            ids = page.find_all(class_='list-identifier')

            n_inds = []
            urls = []
            saved_num = len(p_ids)
            for i,id in enumerate(ids):
                e = id.find(title = 'Abstract')
                id_text = e.text
                url = root_url + e['href']
                urls.append(url)

                if id_text not in p_ids[:saved_num]:
                    p_ids.append(id_text)
                    n_inds.append(i)

            if with_a:
                for ind in n_inds:
                    # p_url = root_url + ids[ind].find(title='Abstract')['href']

                    p_url = urls[ind]
                    soup = get_soup(p_url)
                    title = soup.find(class_='title mathjax').text.lstrip('Title:')
                    abstract = soup.find(class_='abstract mathjax').text

                    paper_content[str(p_count)] = {}
                    paper_content[str(p_count)]['title'] = title
                    paper_content[str(p_count)]['url'] = url
                    paper_content[str(p_count)]['abstract'] = abstract
                    paper_content[str(p_count)]['cite_num'] = -1
                    paper_content[str(p_count)]['conf'] = 'arxiv'
                    paper_content[str(p_count)]['time'] = c_time

                    p_count += 1
                    # print(title)
                    # print(abstract + '\n')

            else:
                papers = page.find_all(class_='meta')
                for ind in n_inds:
                    paper = papers[ind]
                    title = paper.find(class_='list-title mathjax').text.replace('\n','').lstrip('Title: ').lower()
                    url = urls[ind]
                    # citation = soup.find(class_ = 'bib-col-title').text
                    paper_content[str(p_count)] = {}
                    paper_content[str(p_count)]['title'] = title
                    paper_content[str(p_count)]['url'] = url
                    paper_content[str(p_count)]['abstract'] = ''
                    paper_content[str(p_count)]['cite_num'] = -1
                    paper_content[str(p_count)]['conf'] = 'arxiv'
                    paper_content[str(p_count)]['time'] = c_time
                    p_count += 1

                # print(title + '\n')

        with open(f_name,'w') as f:
            json.dump(paper_content,f)
        return paper_content.values()



def mkdir(d_name):
    if not os.path.exists(d_name):
        os.mkdir(d_name)

def gen_times(time_sec,conf_list = []):
    if len(time_sec) == 1:
        if 'arxiv' not in conf_list:
            assert len(time_sec[0]) == 4, 'The time unit for conference should be year! '
            return time_sec

        else:
            if len(time_sec[0]) == 4:

                if type(time_sec) == type((1)):
                    time_sec = list(time_sec)
                time_sec.append(time_sec[0])

                time_sec[0] += '01'
                time_sec[1] += '12'
            else:
                return time_sec

            # assert len(time_sec[0]) == 6, 'The time should be represented by mouth'

    if 'arxiv' in conf_list and len(time_sec[0]) == 4:
        time_sec[0] += '01'
        time_sec[1] += '12'

    if len(time_sec[0]) == 4:
        unit = 'year'
    else:
        unit = 'mouth'

    if unit == 'mouth':
        time_sec[0] = time_sec[0][2:]
        time_sec[1] = time_sec[1][2:]

        sy = int(time_sec[0][:2])
        sm = int(time_sec[0][2:])

        ey = int(time_sec[1][:2])
        em = int(time_sec[1][2:])

        time_list = []
        times = time.strftime('%Y %m %d', time.localtime(time.time())).split()
        sys_time = times[0][2:] + times[1]
        while True:
            if sy > ey or (sy == ey and sm > em):
                break

            s_sy = str(sy)
            s_sm = str(sm)
            if sm < 10:
                s_sm = '0' + s_sm

            c_time = s_sy + s_sm

            if int(sys_time) < int(c_time):
                time_sec[1] = sys_time
                print(c_time + ' is not reached.')
                break

            time_list.append(s_sy + s_sm)

            sm += 1
            if sm > 12:
                sy += 1
                sm = 1

            # print(s_sy + s_sm)
    else:
        time_list = []
        s_time = int(time_sec[0])
        e_time = int(time_sec[1])

        for t in range(s_time,e_time + 1):
            time_list.append(str(t))
    return time_list

def break_line(ab):
    n_ab = ''
    for i, w in enumerate(ab):
        n_ab += w
        if (i + 1)%100 == 0:
            n_ab += '\n'
    return n_ab

def with_keywords(title,keywords):
    for w in keywords['r']:
            if w in title:
                return False


    title = ' ' + title + ' '
    if len(keywords['m']) > 0:
        for w in keywords['m']:
            if w not in title:
                return False

        if len(keywords['c']) == 0:
            return True

    else:
        assert len(keywords['c']) > 0, 'the elements can not be empty'


    for w in keywords['c']:
        if w in title:
            return True


    return False

def get_children_text(soup,screen = True):
    nodes = ['\n','[','=','{']
    texts_list = []
    for i,ch in enumerate(soup.descendants):
        try:
            ch.children
        except:
            # print('children ' + str(i))
            # print(str(ch))
            new_ch = ch
            if len(ch) == 0:
                continue

            for n in nodes:
                if n in new_ch:
                    new_ch = new_ch.replace(n,'')

            if len(ch) - len(new_ch) >= 6 and screen:
                continue


            texts_list.append(ch)
    return texts_list

def get_children_title(soup,screen = True):
    nodes = ['\n', '[', '=', '{']
    title_list = []
    for ch in soup.descendants:
        try:
            # print('title ' + ch['title'])
            t = ch['title']
            new_t = ch['title']
            for n in nodes:
                if n in new_t:
                    new_t = new_t.replace(n,'')

            if len(t) - len(new_t) >= 6 and screen:
                continue

            title_list.append(t)
        except:
            pass
    return title_list

def get_longest_text(t_list):
    m_len = len(t_list[0])
    m_text = t_list[0]
    for text in t_list[1:]:
        if len(text) > m_len:
            m_len = len(text)
            m_text = text
    return m_text

def supply_basic_info(item,conf,refresh_info):
    # abstract

    with_abstract = False
    with_cite = False
    # print(item['title'])
    # print(item['url'])

    if not refresh_info and 'abstract' in item.keys() and len(item['abstract']) > 10:
        with_abstract = True

    if not refresh_info and 'cite_num' in item.keys() and item['cite_num'] >= 0:
        with_cite = True

    if not(with_abstract and with_cite):
        title = item['title']
        root = 'https://cn.bing.com'
        url = root + '/academic/search?q='
        url_title = parse.quote(title)
        url += url_title
        soup = get_soup(url)

    if not with_abstract:
        get_abstract(item,soup,conf)
    if not with_cite:
        get_cite_num(item,soup)
    # print(item['abstract'])

def search_with_keywords(opt):
    keywords = opt.keywords
    time_sec = opt.time_sec
    conf_list = opt.conf_list
    time_list = gen_times(time_sec = time_sec, conf_list = conf_list)
    count_list = []
    t_count_list = []

    conf_info = opt.conf_info
    selected_items = []

    for c_time in time_list:
        count = 0
        t_count = 0
        for conf in conf_list:
            c_count = 0
            print(conf + c_time)
            items = get_titles(conf,conf_info,c_time)
            for item in items:
                t_count += 1
                s_text = item['title']

                with_detail_info = False
                if opt.search_in_abstract:
                    supply_basic_info(item,conf,opt.refresh_info)
                    with_detail_info = True
                    s_text += item['abstract']

                if not with_keywords(s_text, keywords):
                    continue

                count += 1
                c_count += 1

                p_title = item['title']
                if not with_detail_info:
                    p_title = addTips(p_title,keywords)

                print(str(c_count) + '. ' + p_title)
                print(item['url'])
                print('')

                if opt.detail_info:
                    supply_basic_info(item,conf,opt.refresh_info)

                selected_items.append(item)

            cache_info(items, conf, c_time)

        count_list.append(count)
        t_count_list.append(t_count)

    paper_count = sum(count_list)
    print('paper count ' + str(paper_count))
    if paper_count == 0:
        return []

    x = list(range(len(time_list)))

    plt.xticks(x, time_list)
    x_label = ''
    for word in keywords['m']:
        x_label += word + ' '
    for word in keywords['c']:
        x_label += word + ' '

    plt.xlabel(x_label)
    plt.plot(x, count_list)

    r_list = [count_list[i]/t_count_list[i] for i in range(len(t_count_list))]
    mr = max(r_list)
    r_list = [r_list[i]/mr * max(count_list)/2 for i in range(len(t_count_list))]
    plt.plot(x,r_list)
    plt.show()
    plt.savefig('result/trend.png')

    return selected_items

def get_soup(url):
    for i in range(10):
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'html.parser')
            return soup
        except:
            print('the internet is in trouble, try again')
    return None

def get_abstract(item,soup,conf):
    # url = 'http://proceedings.mlr.press/v48/guha16.html'
    # url = 'https://www.ijcai.org/proceedings/2019/419'
    # url = 'https://cn.bing.com/academic/profile?id=e06403eeba6f4f2caa57d899348883fc&encoded=0&v=paper_preview&mkt=zh-cn'

    if conf == 'arxiv':
        p_url = item['url']
        soup = get_soup(p_url)
        ab = soup.find(class_='abstract mathjax').text
        ab = ab.lstrip()
        ab = ab.replace('Abstract:','')
        ab = ab.replace('\n','')
        ab = break_line(ab)
        item['abstract'] = ab
        return ab

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

def minDistance(str1, str2):
    matrix = [[i + j for j in range(len(str2) + 1)] for i in range(len(str1) + 1)]

    for i in range(1, len(str1) + 1):
        for j in range(1, len(str2) + 1):
            if str1[i - 1] == str2[j - 1]:
                d = 0
            else:
                d = 1
            matrix[i][j] = min(matrix[i - 1][j] + 1, matrix[i][j - 1] + 1, matrix[i - 1][j - 1] + d)

    return matrix[len(str1)][len(str2)]

def get_cite_num(p_item,soup):
    cite_num = -1
    items = soup.find_all(class_='aca_algo')[:5]

    for i,item in enumerate(items):
        tmp_title = item.select('h2 > a')[0].text
        minDis = minDistance(p_item['title'], tmp_title.lower())
        if minDis > 70:
            if i != len(items) - 1:
                continue
        try:
            if i == len(items) - 1:
                item = items[0]

            cite_num = 0
            item = item.find(class_='caption_venue')
            for j in range(len(item.contents)):
                value = str(item.contents[j])
                if value.startswith('被'):
                    cite_num = int(item.select('a')[1].text)
                    break
        except:
            pass
        break

    p_item['cite_num'] = cite_num
    return cite_num

def cache_info(items,conf,c_time):
    suffix = ''

    fname = 'papers/' + conf + '/' + c_time + suffix + '.json'
    paper_content = {}
    for p_count, item in enumerate(items):
        paper_content[str(p_count)] = item
    # print(title + '\n')

    with open(fname, 'w') as f:
        json.dump(paper_content, f)