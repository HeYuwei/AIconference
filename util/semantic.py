from . import *
import semanticscholar as sch

cookie = 'tid=rBIABlzmn7k6JQAJA9/FAg==; _ga=GA1.2.1966957177.1570796845; hubspotutk=a769e3e1fae818bbbb4b4bbbad5a5f31; _gid=GA1.2.2121409865.1581331129; __hssrc=1; _hp2_ses_props.2424575119=%7B%22ts%22%3A1581334463796%2C%22d%22%3A%22www.semanticscholar.org%22%2C%22h%22%3A%22%2Fsearch%22%7D; __hstc=132950225.a769e3e1fae818bbbb4b4bbbad5a5f31.1570796846432.1581331137539.1581335879260.3; __hssc=132950225.8.1581335879260; _hp2_props.2424575119=%7B%22feature%3Alibrary_tags%22%3Atrue%2C%22feature%3Apdp_entity_relations%22%3Afalse%2C%22experiment%3Anew_ab_framework_aa%22%3A%22control%22%2C%22experiment%3Aautocomplete%22%3Anull%2C%22feature%3Apdp_citation_intents%22%3Atrue%2C%22Is%2090-day%20Returning%20(Non-BoD)%22%3Afalse%2C%22experiment%3Aauthor_claim_flow%22%3Anull%2C%22feature%3Acopyright_banner%22%3Atrue%2C%22experiment%3Aserp_alert%22%3Anull%2C%22feature%3Aauthor_claim%22%3Atrue%2C%22experiment%3Atest_experiment%22%3Anull%2C%22feature%3Aauthor_claim_link_to_onboarding%22%3Afalse%2C%22feature%3Aalternate_sources%22%3Atrue%2C%22feature%3Aaccount_contact_section%22%3Atrue%2C%22feature%3Amobile_login%22%3Atrue%2C%22feature%3Astatic_login_page%22%3Atrue%2C%22feature%3Apreview_box_entity_stats%22%3Afalse%2C%22feature%3Apdp_paper_faqs_cs_only%22%3Afalse%2C%22experiment%3Anew_ab_framework_mock_ab%22%3A%22test_50%22%2C%22feature%3Aauthor_influence_graph%22%3Atrue%2C%22Is%2014-day%20Returning%20(Non-BoD)%22%3Afalse%2C%22Is%201-day%20Returning%20(Non-BoD)%22%3Afalse%2C%22experiment%3Anull_hypothesis%22%3Anull%2C%22Is%2028-day%20Returning%20(Non-BoD)%22%3Afalse%2C%22feature%3Apdp_paper_faqs%22%3Afalse%2C%22feature%3Arecommender_serp_ad%22%3Afalse%2C%22feature%3Aaccount_management%22%3Atrue%2C%22feature%3Apdp_paper_faqs_numerical_only%22%3Afalse%2C%22feature%3Apdp_scorecard%22%3Atrue%2C%22Is%207-day%20Returning%20(Non-BoD)%22%3Afalse%2C%22feature%3Aemergency_banner%22%3Afalse%2C%22experiment%3Apdp_figure_delayed_load%22%3Anull%2C%22feature%3Ahubspot_newsletter_form%22%3Atrue%2C%22feature%3Aauthor_claim_allow_new_claims%22%3Atrue%2C%22experiment%3Arecommendations_builder_survey%22%3Anull%2C%22feature%3Aadaptive_feed_serp_population%22%3Afalse%2C%22experiment%3Aabstract_highlighter%22%3A%22highlighted_abstract%22%2C%22feature%3Alogin_credentials_form%22%3Afalse%2C%22feature%3Aadaptive_feed%22%3Afalse%2C%22feature%3Asatisfaction_survey%22%3Afalse%2C%22feature%3Aauthor_recommendations%22%3Afalse%2C%22experiment%3Aaugmented_reader_pdp%22%3Anull%2C%22feature%3Aopen_athens_login%22%3Atrue%2C%22feature%3Afaq_contentful%22%3Atrue%2C%22feature%3Aopen_athens_redirect%22%3Atrue%2C%22feature%3Aaugmented_reader%22%3Afalse%2C%22feature%3Alogin_demographics_modal%22%3Atrue%2C%22feature%3Alayover_client%22%3Atrue%2C%22feature%3Asimilar_papers_pdp%22%3Atrue%2C%22feature%3Acognito_login_by_email%22%3Afalse%2C%22feature%3Aserp_swap%22%3Afalse%2C%22tid%22%3A%22rBIABlzeUQcCXAAIBTFYAg%3D%3D%22%2C%22Is%20Signed%20In%22%3Afalse%7D; _hp2_id.2424575119=%7B%22userId%22%3A%222273186662589172%22%2C%22pageviewId%22%3A%22877147075951126%22%2C%22sessionId%22%3A%223922597377684658%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; _gat_gtag_UA_67668211_2=1'

def supply_basic_info(item,conf,refresh_info):
    # abstract
    has_abstract = False
    has_cite = False
    # print(item['title'])
    # print(item['url'])

    if not refresh_info and 'abstract' in item.keys() and len(item['abstract']) > 10:
        has_abstract = True

    if not refresh_info and 'cite_num' in item.keys() and item['cite_num'] >= 0:
        has_cite = True

    if not(has_abstract and has_cite):
        title = item['title']
        root = 'https://www.semanticscholar.org/paper/'
        url = root + 'academic/search?q='
        url_title = parse.quote(title)
        url += url_title
        url += '&sort=relevance'
        soup = get_soup(url)
        get_info(item, soup)


def get_info(item, soup):
    root = 'https://www.semanticscholar.org/paper/'
    paper_data = soup.find_all(class_ = 'search-result-title')
    if len(paper_data) == 0:
        item['cite_num'] = ''
        item['abstract'] = ''
        return;

    first_paper = paper_data[0]
    url = root + first_paper['href']

    soup = get_soup(url)
    if soup is None:
        item['cite_num'] = ''
        item['abstract'] = ''
        return ;

    doi_data = soup.find_all(class_ = 'doi__link')
    if len(doi_data) == 0:
        item['cite_num'] = ''
        item['abstract'] = ''
        return ;

    doi = doi_data[0].text
    paper = sch.paper(doi)
    citation = len(paper['citations'])
    abstract = len(paper['abstract'])
    item['cite_num'] = citation
    item['abstract'] = abstract

