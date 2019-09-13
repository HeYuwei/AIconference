#coding=utf-8
import time
import operator
from apps import stop_words
from util import *
phrase_num = 1
conf = 'cvpr'
time = '2019'
type = 'conf'
print_num = 300

# c_words = ['3-d','3d','segm']
# c_words = ['detection']
# c_words = ['video','classification']
c_words = ['video']

def stat_keywords(type,with_abstract = False,save = False):
    items = get_titles(conf,time,type=type)
    titles = [item[0].lower() for item in items]

    if with_abstract:
        abstracts = [item[2].lower() for item in items]
    else:
        abstracts = []
    titles.extend(abstracts)

    p_stat = {}
    dots = ';,:.?'
    for dot in dots:
        titles = [title.replace(dot, '') for title in titles]

    for title in titles:
        with_c = False
        if len(c_words) > 0:
            for c_word in c_words:
                if c_word in title:
                    with_c = True
                    break
        else:
            with_c = True

        if not with_c:
            continue

        words = title.split()
        n_words = []
        if phrase_num == 1:
            for word in words:
                if word not in stop_words.stop_words:
                    n_words.append(word)
        words = n_words

        for i in range(len(words) - phrase_num + 1):
            phrase = ''
            for j in range(phrase_num):
                phrase += words[i + j]
                phrase += ' '
            phrase = phrase[:-1]
            if phrase not in p_stat.keys():
                p_stat[phrase] = 1
            else:
                p_stat[phrase] += 1

    p_stat = sorted(p_stat.items(), key=operator.itemgetter(1), reverse=True)

    for phrase, count in p_stat[:print_num]:
        print(phrase + ' ' + str(count))

    if save:
        mkdir('keywords')
        save_name = 'keywords/' + conf + time
        if with_abstract:
            save_name += 'a'
        save_name += '.txt'
        with open('keywords/' + conf + time + '.txt','w') as f:
            for phrase, count in p_stat:
                # print(phrase + ' ' + str(count))
                f.write(phrase + ' ' + str(count) + '\n')

if __name__ == '__main__':
    stat_keywords(type = type,save = False)