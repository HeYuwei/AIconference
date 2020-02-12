from .basic import *
from .bing import supply_basic_info



def search_with_keywords(opt):
    keywords = opt.keywords
    time_sec = opt.time_sec
    conf_list = opt.conf_list
    time_list = gen_times(time_sec = time_sec, conf_list = conf_list)

    year_selected_count_list = []
    year_total_count_list = []

    conf_info = opt.conf_info
    selected_items = []

    def is_target_item(item):
        with_ab = False
        s_text = item['title']

        if opt.search_in_abstract:
            supply_basic_info(item,conf,opt.refresh_info)
            s_text += item['abstract']
            with_ab = True

        if not with_keywords(s_text, keywords):
            return (0,item)

        if opt.supply_detail_info and not with_ab:
            supply_basic_info(item,conf,opt.refresh_info)

        return (1, item)

    for c_time in time_list:
        year_selected_count = 0
        year_total_count = 0
        for conf in conf_list:
            conf_selected_count = 0
            print(conf + c_time)
            items = get_titles(conf,conf_info,c_time)

            tmp_data_list = read_multi_data(is_target_item, items, workers = 100)
            indicators = []
            items = []

            for tmp_data in tmp_data_list:
                indicators.append(tmp_data[0])
                items.append(tmp_data[1])

            assert len(indicators) == len(items)
            # for item in items:
            #     with_ab = False
            #     year_total_count += 1
            #     s_text = item['title']
            #
            #     if opt.search_in_abstract:
            #         supply_basic_info(item,conf,opt.refresh_info)
            #         s_text += item['abstract']
            #         with_ab = True
            #
            #     if not with_keywords(s_text, keywords):
            #         continue
            #
            #     year_selected_count += 1
            #     conf_selected_count += 1
            #
            #     p_title = item['title']
            #     if opt.with_tip:
            #         p_title = addTips(p_title,keywords)
            #
            #     print(str(conf_selected_count) + '. ' + p_title)
            #     print(item['url'])
            #     print('')
            #
            #     if opt.supply_detail_info and not with_ab:
            #         supply_basic_info(item,conf,opt.refresh_info)
            #
            #     selected_items.append(item)
            #

            tmp_selected_items = [items[i] for i in range(len(indicators)) if indicators[i]]
            selected_items.extend(tmp_selected_items)

            year_selected_count += len(tmp_selected_items)
            year_total_count += len(items)
            conf_selected_count += len(tmp_selected_items)

            cache_info(items, conf, c_time)

        year_selected_count_list.append(year_selected_count)
        year_total_count_list.append(year_total_count)

    paper_count = sum(year_selected_count_list)
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
    plt.plot(x, year_selected_count_list)

    r_list = [year_selected_count_list[i]/year_total_count_list[i] for i in range(len(year_total_count_list))]
    mr = max(r_list)
    r_list = [r_list[i]/mr * max(year_selected_count_list)/2 for i in range(len(year_total_count_list))]
    plt.plot(x,r_list)
    plt.show()
    plt.savefig('result/trend.png')

    return selected_items

def search_with_keywords_parallel(opt):
    keywords = opt.keywords
    time_sec = opt.time_sec
    conf_list = opt.conf_list
    time_list = gen_times(time_sec = time_sec, conf_list = conf_list)

    conf_info = opt.conf_info
    tmp_params_list = []
    for c_time in time_list:
        for conf in conf_list:
            tmp_params_list.append([conf, conf_info, c_time])

    paper_data = read_multi_data(get_titles,tmp_params_list, workers=100)
    print('All conferences are loaded')
    items = []
    for tmp_data in paper_data:
        items += tmp_data
    print('There are ', len(items), ' papers in total')

    def is_target_item(item):
        with_ab = False
        s_text = item['title']

        if opt.search_in_abstract:
            supply_basic_info(item,conf,opt.refresh_info)
            s_text += item['abstract']
            with_ab = True

        if not with_keywords(s_text, keywords):
            return (0,item)

        if opt.supply_detail_info and not with_ab:
            supply_basic_info(item,conf,opt.refresh_info)

        return (1, item)


    tmp_data_list = read_multi_data(is_target_item, items, workers = 100)
    indicators = []
    items = []
    for tmp_data in tmp_data_list:
        indicators.append(tmp_data[0])
        items.append(tmp_data[1])

    print('indicator len ', len(indicators))
    print('items ', len(items))
    assert len(indicators) == len(items)

    for c_time in time_list:
        for conf in conf_list:
            cache_info(items, conf, c_time)

    selected_items = [items[i] for i in range(len(indicators)) if indicators[i]]
    total_items = items

    def get_count_per_year(items):
        count_list = [0] * len(time_list)
        for item in items:
            c_time = item['time']
            ind = time_list.index(c_time)
            count_list[ind] += 1
        return count_list

    year_selected_count_list = get_count_per_year(selected_items)
    year_total_count_list = get_count_per_year(total_items)

    paper_count = len(selected_items)
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
    plt.plot(x, year_selected_count_list)

    r_list = [year_selected_count_list[i]/year_total_count_list[i] for i in range(len(year_total_count_list))]
    mr = max(r_list)
    r_list = [r_list[i]/mr * max(year_selected_count_list)/2 for i in range(len(year_total_count_list))]
    plt.plot(x,r_list)
    plt.show()
    plt.savefig('result/trend.png')

    return selected_items


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

    if c_time == sys_time and os.path.exists(f_name):
        os.system('rm ' + f_name)

    if os.path.exists(f_name):
    # if False:
        with open(f_name,'r') as f:
            data = json.load(f)
            print('arxiv', c_time, ' is loaded')
            return list(data.values())
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

            all_parts = page.select('small')
            page_scale = all_parts[0]

            def get_entry_num(text):
                tmp_list = text.split(' ')
                e_ind = tmp_list.index('entries:')
                return int(tmp_list[e_ind - 1])
            entry_num = get_entry_num(page_scale.text)
            page_ind_parts = all_parts[1]

            # if len(page_scale.select('a')) >= 2:
            if True:
                # all_url = page_scale.select('a')[2]['href']
                # url = root_url + all_url
                url += '?show=' + str(entry_num)
                soup = get_soup(url)
                page = soup.find(id='dlpage')
                ids = page.find_all(class_='list-identifier')
            else:
                page = []
                ids = []
                for page_ind_part in page_ind_parts:
                    page_url = page_ind_part['href']
                    url = root_url + page_url
                    soup = get_soup(url)
                    tmp_page = soup.find(id='dlpage')
                    tmp_ids = tmp_page.find_all(class_='list-identifier')
                    page.extend(tmp_page)
                    ids.extend(tmp_ids)

            n_inds = []
            cur_p_ids = []
            urls = []
            saved_num = len(p_ids)

            for i,id in enumerate(ids):
                e = id.find(title = 'Abstract')
                id_text = e.text
                url = root_url + e['href']
                urls.append(url)
                cur_p_ids.append(id_text)

                if id_text not in p_ids[:saved_num]:
                    p_ids.append(id_text)
                    n_inds.append(i)

            if with_a:

                def get_tmp_info(ind):
                    p_url = urls[ind]
                    soup = get_soup(p_url)
                    title = soup.find(class_='title mathjax').text.lstrip('Title:')
                    abstract = soup.find(class_='abstract mathjax').text
                    tmp_data = {}
                    tmp_data['title'] = title
                    tmp_data['url'] = url
                    tmp_data['abstract'] = abstract
                    tmp_data['cite_num'] = -1
                    tmp_data['conf'] = 'arxiv'
                    tmp_data['time'] = c_time
                    return data

                paper_data = read_multi_data(get_tmp_info, n_inds)
                for tmp_data in paper_data:
                    paper_content[str(p_count)] = tmp_data
                    p_count += 1

                # for ind in n_inds:
                #     p_url = urls[ind]
                #     soup = get_soup(p_url)
                #     title = soup.find(class_='title mathjax').text.lstrip('Title:')
                #     abstract = soup.find(class_='abstract mathjax').text
                #
                #     paper_content[str(p_count)] = {}
                #     paper_content[str(p_count)]['title'] = title
                #     paper_content[str(p_count)]['url'] = url
                #     paper_content[str(p_count)]['abstract'] = abstract
                #     paper_content[str(p_count)]['cite_num'] = -1
                #     paper_content[str(p_count)]['conf'] = 'arxiv'
                #     paper_content[str(p_count)]['time'] = c_time
                #
                #     p_count += 1
                #     # print(title)
                #     # print(abstract + '\n')
                #
            else:
                papers = page.find_all(class_='meta')
                for ind in n_inds:
                    doi = cur_p_ids[ind]
                    paper = papers[ind]
                    title = paper.find(class_='list-title mathjax').text.replace('\n','').lstrip('Title: ').lower()
                    url = urls[ind]
                    # citation = soup.find(class_ = 'bib-col-title').text
                    paper_content[str(p_count)] = {}
                    paper_content[str(p_count)]['title'] = title
                    paper_content[str(p_count)]['doi'] = doi
                    paper_content[str(p_count)]['url'] = url
                    paper_content[str(p_count)]['abstract'] = ''
                    paper_content[str(p_count)]['cite_num'] = -1
                    paper_content[str(p_count)]['conf'] = 'arxiv'
                    paper_content[str(p_count)]['time'] = c_time
                    p_count += 1

                # print(title + '\n')

        with open(f_name,'w') as f:
            json.dump(paper_content,f)
        print('arxiv', c_time, ' is loaded')
        return list(paper_content.values())

def get_titles(conf ,conf_info, c_time):
    with_a = False
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
            return list(data.values())
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
            v_ind = 2020 - int(c_time)
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

            print('The papers in ' + conf + c_time + ' are loaded')
            return list(content.values())

