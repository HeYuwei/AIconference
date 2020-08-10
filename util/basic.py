import torch.multiprocessing as multiprocessing
import urllib
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

def one_page_titles(conf, conf_info, c_time, volume = ''):

    url = 'https://dblp.org/db/' + conf_info[conf]['type'] + '/' + conf_info[conf]['parent'] + '/' + conf + c_time + volume + '.html'
    soup = get_soup(url)

    if conf_info[conf]['type'] == 'conf':
        items = soup.find_all(class_='entry inproceedings')
    else:
        items = soup.find_all(class_='entry article')

    titles = []
    for item in items:
        title = item.find(class_ = 'title').text.lower()
        url = item.find(class_ = 'ee').find('a').get('href')
        titles.append((title, url))
    return titles

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
    line_w_count = 0
    ab = ab.replace('\t','')
    for i, w in enumerate(ab):
        n_ab += w
        line_w_count += 1
        if w == '\n':
            line_w_count = 0
        if line_w_count == 100:
            n_ab += '\n'
            line_w_count = 0
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

def get_soup(url):
    for i in range(10):
        try:
        #     req = urllib.request.Request(url)
            header = {}
            # header['user-agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
            # header['authority'] = 'www.semanticscholar.org'
            # header['cookie'] = 'sid=37e31b1f-5a92-4bef-b584-73f291bf6eca; tid=rBIABlzeUQcCXAAIBTFYAg==; _ga=GA1.2.1966957177.1570796845; hubspotutk=a769e3e1fae818bbbb4b4bbbad5a5f31; s2Hist=2020-02-10T00%3A00%3A00.000Z%7C1; _gid=GA1.2.2121409865.1581331129; sid=37e31b1f-5a92-4bef-b584-73f291bf6eca; compact_serp_results=false; __hssrc=1; __hstc=132950225.a769e3e1fae818bbbb4b4bbbad5a5f31.1570796846432.1581331137539.1581335879260.3; s2Exp=new_ab_framework_aa%3Dcontrol%26new_ab_framework_mock_ab%3Dtest_50%26title_search%3D-with_title_search%26serp_density%3D-control%26abstract_highlighter%3Dhighlighted_abstract; _hp2_props.2424575119=%7B%22feature%3Alibrary_tags%22%3Atrue%2C%22feature%3Apdp_entity_relations%22%3Afalse%2C%22experiment%3Anew_ab_framework_aa%22%3A%22control%22%2C%22experiment%3Aautocomplete%22%3Anull%2C%22feature%3Apdp_citation_intents%22%3Atrue%2C%22Is%2090-day%20Returning%20(Non-BoD)%22%3Afalse%2C%22experiment%3Aauthor_claim_flow%22%3Anull%2C%22feature%3Acopyright_banner%22%3Atrue%2C%22experiment%3Aserp_alert%22%3Anull%2C%22feature%3Aauthor_claim%22%3Atrue%2C%22experiment%3Atest_experiment%22%3Anull%2C%22feature%3Aauthor_claim_link_to_onboarding%22%3Afalse%2C%22feature%3Aalternate_sources%22%3Atrue%2C%22feature%3Aaccount_contact_section%22%3Atrue%2C%22feature%3Amobile_login%22%3Atrue%2C%22feature%3Astatic_login_page%22%3Atrue%2C%22feature%3Apreview_box_entity_stats%22%3Afalse%2C%22feature%3Apdp_paper_faqs_cs_only%22%3Afalse%2C%22experiment%3Anew_ab_framework_mock_ab%22%3A%22test_50%22%2C%22feature%3Aauthor_influence_graph%22%3Atrue%2C%22Is%2014-day%20Returning%20(Non-BoD)%22%3Afalse%2C%22Is%201-day%20Returning%20(Non-BoD)%22%3Afalse%2C%22experiment%3Anull_hypothesis%22%3Anull%2C%22Is%2028-day%20Returning%20(Non-BoD)%22%3Afalse%2C%22feature%3Apdp_paper_faqs%22%3Afalse%2C%22feature%3Arecommender_serp_ad%22%3Afalse%2C%22feature%3Aaccount_management%22%3Atrue%2C%22feature%3Apdp_paper_faqs_numerical_only%22%3Afalse%2C%22feature%3Apdp_scorecard%22%3Atrue%2C%22Is%207-day%20Returning%20(Non-BoD)%22%3Afalse%2C%22feature%3Aemergency_banner%22%3Afalse%2C%22experiment%3Apdp_figure_delayed_load%22%3Anull%2C%22feature%3Ahubspot_newsletter_form%22%3Atrue%2C%22feature%3Aauthor_claim_allow_new_claims%22%3Atrue%2C%22experiment%3Arecommendations_builder_survey%22%3Anull%2C%22feature%3Aadaptive_feed_serp_population%22%3Afalse%2C%22experiment%3Aabstract_highlighter%22%3A%22highlighted_abstract%22%2C%22feature%3Alogin_credentials_form%22%3Afalse%2C%22feature%3Aadaptive_feed%22%3Afalse%2C%22feature%3Asatisfaction_survey%22%3Afalse%2C%22feature%3Aauthor_recommendations%22%3Afalse%2C%22experiment%3Aaugmented_reader_pdp%22%3Anull%2C%22feature%3Aopen_athens_login%22%3Atrue%2C%22feature%3Afaq_contentful%22%3Atrue%2C%22feature%3Aopen_athens_redirect%22%3Atrue%2C%22feature%3Aaugmented_reader%22%3Afalse%2C%22feature%3Alogin_demographics_modal%22%3Atrue%2C%22feature%3Alayover_client%22%3Atrue%2C%22feature%3Asimilar_papers_pdp%22%3Atrue%2C%22feature%3Acognito_login_by_email%22%3Afalse%2C%22feature%3Aserp_swap%22%3Afalse%2C%22tid%22%3A%22rBIABlzeUQcCXAAIBTFYAg%3D%3D%22%2C%22Is%20Signed%20In%22%3Afalse%7D; _hp2_id.2424575119=%7B%22userId%22%3A%222273186662589172%22%2C%22pageviewId%22%3A%224634628218095506%22%2C%22sessionId%22%3A%222426040208247647%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; _hp2_ses_props.2424575119=%7B%22ts%22%3A1581341143973%2C%22d%22%3A%22www.se' \
            #                    'manticscholar.org%22%2C%22h%22%3A%22%2Fsearch%22%7D; _gat_gtag_UA_67668211_2=1'
            # header['authority'] = 'www.semanticscholar.org'
            # header['method'] = 'GET'
            # header['path'] = '/search?q=The%20separation%20of%20ownership%20and%20control%20in%20East%20Asian%20Corporations&sort=relevance'
            # header['scheme'] = 'https'
            # header['accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
            # header['accept-encoding'] = 'gzip, deflate, br'
            # header['accept-language'] = 'zh-CN,zh;q=0.9'
            # header['cache-control'] = 'max-age=0'
            # header['cookie'] = 'tid=rBIABlzeUQcCXAAIBTFYAg==; _ga=GA1.2.1966957177.1570796845; hubspotutk=a769e3e1fae818bbbb4b4bbbad5a5f31; s2Hist=2020-02-10T00%3A00%3A00.000Z%7C1; _gid=GA1.2.2121409865.1581331129; sid=37e31b1f-5a92-4bef-b584-73f291bf6eca; compact_serp_results=false; __hssrc=1; s2Exp=new_ab_framework_aa%3Dcontrol%26new_ab_framework_mock_ab%3Dtest_50%26title_search%3D-with_title_search%26serp_density%3D-control%26abstract_highlighter%3Dhighlighted_abstract; _hp2_props.2424575119=%7B%22feature%3Alibrary_tags%22%3Atrue%2C%22feature%3Apdp_entity_relations%22%3Afalse%2C%22experiment%3Anew_ab_framework_aa%22%3A%22control%22%2C%22experiment%3Aautocomplete%22%3Anull%2C%22feature%3Apdp_citation_intents%22%3Atrue%2C%22Is%2090-day%20Returning%20(Non-BoD)%22%3Afalse%2C%22experiment%3Aauthor_claim_flow%22%3Anull%2C%22feature%3Acopyright_banner%22%3Atrue%2C%22experiment%3Aserp_alert%22%3Anull%2C%22feature%3Aauthor_claim%22%3Atrue%2C%22experiment%3Atest_experiment%22%3Anull%2C%22feature%3Aauthor_claim_link_to_onboarding%22%3Afalse%2C%22feature%3Aalternate_sources%22%3Atrue%2C%22feature%3Aaccount_contact_section%22%3Atrue%2C%22feature%3Amobile_login%22%3Atrue%2C%22feature%3Astatic_login_page%22%3Atrue%2C%22feature%3Apreview_box_entity_stats%22%3Afalse%2C%22feature%3Apdp_paper_faqs_cs_only%22%3Afalse%2C%22experiment%3Anew_ab_framework_mock_ab%22%3A%22test_50%22%2C%22feature%3Aauthor_influence_graph%22%3Atrue%2C%22Is%2014-day%20Returning%20(Non-BoD)%22%3Afalse%2C%22Is%201-day%20Returning%20(Non-BoD)%22%3Afalse%2C%22experiment%3Anull_hypothesis%22%3Anull%2C%22Is%2028-day%20Returning%20(Non-BoD)%22%3Afalse%2C%22feature%3Apdp_paper_faqs%22%3Afalse%2C%22feature%3Arecommender_serp_ad%22%3Afalse%2C%22feature%3Aaccount_management%22%3Atrue%2C%22feature%3Apdp_paper_faqs_numerical_only%22%3Afalse%2C%22feature%3Apdp_scorecard%22%3Atrue%2C%22Is%207-day%20Returning%20(Non-BoD)%22%3Afalse%2C%22feature%3Aemergency_banner%22%3Afalse%2C%22experiment%3Apdp_figure_delayed_load%22%3Anull%2C%22feature%3Ahubspot_newsletter_form%22%3Atrue%2C%22feature%3Aauthor_claim_allow_new_claims%22%3Atrue%2C%22experiment%3Arecommendations_builder_survey%22%3Anull%2C%22feature%3Aadaptive_feed_serp_population%22%3Afalse%2C%22experiment%3Aabstract_highlighter%22%3A%22highlighted_abstract%22%2C%22feature%3Alogin_credentials_form%22%3Afalse%2C%22feature%3Aadaptive_feed%22%3Afalse%2C%22feature%3Asatisfaction_survey%22%3Afalse%2C%22feature%3Aauthor_recommendations%22%3Afalse%2C%22experiment%3Aaugmented_reader_pdp%22%3Anull%2C%22feature%3Aopen_athens_login%22%3Atrue%2C%22feature%3Afaq_contentful%22%3Atrue%2C%22feature%3Aopen_athens_redirect%22%3Atrue%2C%22feature%3Aaugmented_reader%22%3Afalse%2C%22feature%3Alogin_demographics_modal%22%3Atrue%2C%22feature%3Alayover_client%22%3Atrue%2C%22feature%3Asimilar_papers_pdp%22%3Atrue%2C%22feature%3Acognito_login_by_email%22%3Afalse%2C%22feature%3Aserp_swap%22%3Afalse%2C%22tid%22%3A%22rBIABlzeUQcCXAAIBTFYAg%3D%3D%22%2C%22Is%20Signed%20In%22%3Afalse%2C%22experiment%3Atitle_search%22%3Anull%2C%22experiment%3Aserp_density%22%3Anull%7D; __hstc=132950225.a769e3e1fae818bbbb4b4bbbad5a5f31.1570796846432.1581335879260.1581341318701.4; _gat_gtag_UA_67668211_2=1; _hp2_ses_props.2424575119=0; _hp2_id.2424575119=%7B%22userId%22%3A%222273186662589172%22%2C%22pageviewId%22%3A%221421177729073429%22%2C%22sessionId%22%3A%225915959417396478%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D'
            # header['sec-fetch-mode'] = 'navigate'
            # header['sec-fetch-site'] = 'none'
            # header['sec-fetch-user'] = '?1'
            # header['upgrade-insecure-requests'] = '1'
            # header['user-agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
            # response = urllib.request.urlopen(req)
            # html = response.read()
            # soup = BeautifulSoup(html, "html.parser")

            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'html.parser')
            return soup
        except:
            print('the internet is in trouble, try again')
    return None

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

def cache_info(items,conf,c_time):
    if len(items) == 0:
        return
    # assert len(items) > 0
    items = list(filter(lambda x: x['conf'] == conf and x['time'] == c_time, items))
    suffix = ''
    fname = 'papers/' + conf + '/' + c_time + suffix + '.json'
    paper_content = {}
    for p_count, item in enumerate(items):
        paper_content[str(p_count)] = item
    # print(title + '\n')

    with open(fname, 'w') as f:
        json.dump(paper_content, f)

def read_multi_data(func, param_list, workers = 3, ignore_none = True):
    import tqdm
    param_data = [[] for _ in range(workers)]
    c_worker = 0
    for i, param in enumerate(param_list):
        param_data[c_worker].append((i,param))
        c_worker = (c_worker + 1) % workers

    q = multiprocessing.Queue()
    q.cancel_join_thread()

    count = 0

    def read_data(func, param_part_list):

        if len(param_part_list) > 100:
            param_part_list = tqdm.tqdm(param_part_list)
        for i, param in param_part_list:
            try:
                if isinstance(param,list):
                    data = func(*param)
                else:
                    data = func(param)
            except:
                data = None

            q.put((i, data))

    for i in range(workers):
        w = multiprocessing.Process(
            target=read_data,
            args=(func, param_data[i]))
        w.daemon = False
        w.start()

    data_list = [None for _ in range(len(param_list))]

    while count < len(param_list):
        i, data = q.get()
        data_list[i] = data
        count += 1

    new_data_list = []
    if ignore_none:
        for data in data_list:
            if data is not None:
                new_data_list.append(data)
        data_list = new_data_list

    return data_list

