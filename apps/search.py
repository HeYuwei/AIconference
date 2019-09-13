from util import search_with_keywords
import numpy as np


def search(opt):
    select_items = search_with_keywords(opt)

    if len(select_items) == 0:
        print('There is no paper.')
        return ;

    if not opt.detail_info:
        print('There is no detailed info to show.')
        return ;

    if opt.show_order == 'cite_num':
        cite_list = [item['cite_num'] for item in select_items]
        sort_inds = np.argsort(-np.array(cite_list))
        sort_inds = sort_inds.tolist()


        for i, ind in enumerate(sort_inds):
            item = select_items[ind]
            print(str(i + 1) + '. ' + item['title'])
            print(item['url'])
            print('被引数：' + str(item['cite_num']) + '    ' + item['conf'] + item['time'])
            print('Abstract')
            print(item['abstract'])
            print('\n')

    elif opt.show_order == 'time':

        item = select_items[0]
        c_conf = item['conf'] + item['time']
        print(c_conf)
        c_count = 1
        for item in select_items:
            tmp_conf = item['conf'] + item['time']
            if tmp_conf != c_conf:
                c_count = 1
                c_conf = tmp_conf
                print(c_conf)
            print(str(c_count) + '. ' + item['title'])
            print(item['url'])
            print('被引数：' + str(item['cite_num']))
            print('Abstract')
            print(item['abstract'])
            print('\n')
            c_count += 1