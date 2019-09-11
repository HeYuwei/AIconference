from util import *
import matplotlib.pyplot as plt

# 所要查找会议名称
conf_list = ['cvpr','iccv','eccv','aaai','ijcai','nips','icml','iclr', 'mm']
# conf_list = ['cvpr']
conf_list = ['arxiv']
# 时间范围，以年为单位，arxiv以月为单位
# time_sec = ['2016','2019']
time_sec = ['201701','201909']
# 是否在摘要中检索关键字
with_abstract = False
# 是否标记关键字
with_tip = False
# 是否显示引用数
print_cite_num = True
# 是否显示摘要
print_abstract = True

# 是否刷新本地信息
refresh_info = False

# 所要检索的关键字
keywords = {}
keywords['m'] = []
keywords['c'] = []
keywords['r'] = []
keywords['c'] = ['anoma','unusua','abnor','viole']
# keywords['c'] = ['encoder']

conf_info = init_conf_info()

def assert_info():
    if len(conf_list) > 1 and 'arxiv' in conf_list:
        assert False, 'arxiv must be acount solely!'
    recorded_confs =  list(conf_info.keys())
    # print(str(recorded_confs))
    for conf in conf_list:
        if conf not in recorded_confs:
            assert False, 'The info of ' + conf + ' must be recorded first!'

    for t in time_sec:
        assert len(t) == 4 or len(t) == 6, 'The time unit should be year or mouth'

def stat_with_keywords(keywords):
    time_list = gen_times(time_sec = time_sec, conf_list = conf_list)
    count_list = []
    t_count_list = []

    for time in time_list:
        count = 0
        t_count = 0
        for conf in conf_list:
            c_count = 0
            print(conf + time)
            items = get_titles(conf,conf_info,time)
            for item in items:
                t_count += 1
                s_text = item['title']
                if not with_keywords(s_text, keywords):
                    continue

                supply_basic_info(item,conf,refresh_info)
                count += 1
                c_count += 1

                p_title = item['title']
                if with_tip:
                    p_title = addTips(p_title,keywords)

                print(str(c_count) + '. ' + p_title)
                print(item['url'])
                if print_cite_num:
                    cite_num = item['cite_num']
                    print('被引数：' + str(cite_num))

                if print_abstract:
                    ab = item['abstract']
                    print('Abstract')
                    print(ab)

                print('\n')

            cache_info(items, conf, time, with_ab=with_abstract)

        count_list.append(count)
        t_count_list.append(t_count)

    print('paper count ' + str(sum(count_list)))

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
    plt.savefig('trend.png')


if __name__ == '__main__':
    assert_info()
    stat_with_keywords(keywords)
