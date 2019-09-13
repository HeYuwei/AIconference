import argparse
from util import ex_funtion, assert_info, init_conf_info

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, conflict_handler="resolve")
    parser.add_argument('--conf_list', type = object , default=['cvpr','iccv','eccv','aaai','ijcai','nips','icml','iclr','mm'],
                        help='The conferences or journal to reserach.')

    parser.add_argument('--time_sec', type = object, default=['2016','2019'],
                        help= 'The time range to research')

    parser.add_argument('--with_tip', type=bool, default=False,
                        help='Note the keywords.')

    parser.add_argument('--key_words_m', type=list, default=['attention'],
                        help='The words must be contained ')
    parser.add_argument('--key_words_c', type=list, default=[],
                        help='The words could be contained ')
    parser.add_argument('--key_words_r', type=list, default=[],
                        help='The words can not be contained ')

    parser.add_argument('--detail_info', type=bool, default=True,
                        help='function to perform')

    parser.add_argument('--refresh_info', type=bool, default=False,
                        help='Refresh local info ')

    parser.add_argument('--show_order', type=str, default='time', choices=['cite_num','time'],
                        help='the order to show papers ')

    parser.add_argument('--function', type=str, default='search', choices=['search'],
                        help='function to perform')

    opt = parser.parse_args()

    opt.conf_info = init_conf_info()
    assert_info(opt)
    ex_funtion(opt)


