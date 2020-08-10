from util.basic import get_soup, read_multi_data

import sys
sys.setrecursionlimit(100000)

def get_medhub_info(conf, year, conf_info):
    search_url = 'https://pubmed.ncbi.nlm.nih.gov/?term=%22' + conf_info[conf]['parent'] + '%22%5BJour%5D+%22' + str(year) + '%22%5BDP%5D'

    b_url = 'https://doi.org/'

    all_items = []
    page = 1
    while True:
        tmp_url = search_url + '&page=' + str(page)
        soup = get_soup(tmp_url)
        tmp_items = soup.find_all(class_='docsum-wrap')
        if len(tmp_items) == 0:
            break
        all_items.extend(tmp_items)
        page += 1


    # def read_doc_items(page):
    #     tmp_url = search_url + '&page=' + str(page)
    #     soup = get_soup(tmp_url)
    #     tmp_items = soup.find_all(class_='docsum-wrap')
    #     return tmp_items
    #
    # tmp_items = read_doc_items(1)
    # all_items.extend(tmp_items)
    # soup = get_soup(search_url)
    # paper_num = soup.select('div.results-amount > span.value')[0].text.replace(',', '')
    # paper_num = int(paper_num)
    #
    # page_num = paper_num // 10 + int(paper_num % 10 != 0) - 1
    # page_list = list(range(2, 2 +10))

    # tmp_items_data = read_multi_data(read_doc_items, param_list=page_list, workers=5)
    # for tmp_items in tmp_items_data:
    #     all_items += tmp_items

    all_data = []

    for item in all_items:
        title = item.find(class_ = 'docsum-title').text.lstrip().rstrip().lower()
        tmp_text = item.find(class_ = 'docsum-journal-citation full-journal-citation').text
        doi_ind = tmp_text.index('doi:')
        tmp_text = tmp_text[doi_ind + 4:]
        doi = tmp_text.split()[0][:-1]
        url = b_url + doi

        all_data.append([title, doi, url])

    return all_data

