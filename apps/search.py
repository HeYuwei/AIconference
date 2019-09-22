from util import search_with_keywords,gen_save_name
import numpy as np


def search(opt):
    select_items = search_with_keywords(opt)

    if len(select_items) == 0:
        print('There is no paper.')
        return ;

    if not opt.detail_info:
        print('There is no detailed info to show.')
        return ;

    save_name  = gen_save_name(opt,'search')

    f = open('result/' + save_name + '.txt','w',encoding='utf8')

    if opt.show_order == 'cite_num':
        cite_list = [item['cite_num'] for item in select_items]
        sort_inds = np.argsort(-np.array(cite_list))
        sort_inds = sort_inds.tolist()


        for i, ind in enumerate(sort_inds):
            item = select_items[ind]
            line = ''
            line += str(i + 1) + '. ' + item['title']
            line += '\n'
            line += item['url']
            line += '\n'
            line += '被引数：' + str(item['cite_num']) + '    ' + item['conf'] + item['time']
            line += '\n'
            line += 'Abstract'
            line += '\n'
            line += item['abstract']
            line += '\n\n'
            try:
                print(line)
                f.write(line)
            except:
                pass


    elif opt.show_order == 'time':

        item = select_items[0]
        c_conf = item['conf'] + item['time']
        f.write(c_conf + '\n')
        print(c_conf)
        c_count = 1
        for item in select_items:
            tmp_conf = item['conf'] + item['time']
            if tmp_conf != c_conf:
                c_count = 1
                c_conf = tmp_conf
                f.write(c_conf + '\n')
                print(c_conf)

            line = ''
            line += str(c_count) + '. ' + item['title']
            line += '\n'
            line += item['url']
            line += '\n'
            line += '被引数：' + str(item['cite_num'])
            line += '\n'
            line += 'Abstract'
            line += '\n'
            line += item['abstract']
            line += '\n\n'
            c_count += 1
            print(line)
            f.write(line)

    f.close()