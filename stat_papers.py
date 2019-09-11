from util import *

phrase_num = 1
conf = 'ijcai'
time = '2018'
type = 'conf'
volume = ''
keywords = ['nois']

def stat_with_keywords(keywords):
    items = get_titles(conf,time,type=type)
    count = 1
    for item in items:
        p = False
        for keyword in keywords:
            if keyword not in item[0]:
                p = True
                break
        if p:
            continue

        print(str(count) + '. ' + item[0])
        print(item[1])
        print('\n')
        count += 1

if __name__ == '__main__':
    stat_with_keywords(keywords)