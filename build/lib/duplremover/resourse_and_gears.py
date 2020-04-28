import logging
import re
import sys
import time

from duplremover.set_logger import set_logger

front_codes = {"red": 31, "black": 30, "green": 32, "yellow": 33, "blue": 34, 'magenta': 35, "cyan": 36, "while": 37, "ordinary": 38}
back_codes = {"red": 41, "black": 40, "green": 42, "yellow": 43, "blue": 44, 'magenta': 45, "cyan": 46, "while": 47, "ordinary": 48}
show_modes = {"default": 0, "highlight": 1, "non-highlight": 22, "underline": 4, "non_underline": 24,
              "blinking": 5, "non-blinking": 25, "reverse": 7, "non-reverse": 27, "invisible": 8, 'visible': 28}


log_level = logging.INFO
LOGGER = set_logger(log_level)


def note_printer(print_list, start_num=0, top_note=None, end_note=None, fill_str='*', disordered_mode=False,
                 top_note_color="ordinary", front_color='ordinary', back_color='ordinary', show_mode="default"):
    """
    :param top_note_color:
    :param show_mode:
    :param back_color:
    :param front_color:
    :param print_list:  需要打印的列表，列表元素任意
    :param start_num:  按行打印时的开始编号
    :param top_note:  开始打印前的提示字符串
    :param end_note:  结束字符串
    :param fill_str:  开始行和结束行的空白处填充字符
    :param disordered_mode:  无序模式
    :return:
    """
    tnc = front_codes.get(top_note_color, 38)
    fc = front_codes.get(front_color, 38)
    bc = back_codes.get(back_color, 48)
    sm = show_modes.get(show_mode, 0)
    max_len = max([len(str(re.sub(r'[\u4e00-\u9fa5]+', '', x)))+len(''.join(re.findall(r'[\u4e00-\u9fa5]+', x)))*1.7
                   for x in print_list]) + 6
    top_note = ' list printer '.format(str(print_list)[0:10]) if top_note is None else f' {top_note} '
    end_note = '' if end_note is None else ' {} '.format(end_note)
    note_len = max([len(top_note), len(end_note)]) + 6
    max_len = note_len if int(max_len) <= note_len else int(max_len)
    top_out = ('{:%s^%d}' % (fill_str, max_len)).format(top_note)
    end_out = ('{:%s^%d}' % (fill_str, max_len)).format(end_note)
    printer(' ')
    printer(top_out)
    if not disordered_mode:
        for i, v in enumerate(print_list, start=start_num):
            out_str = f' {i} : \033[{sm};{fc};{bc}m{v}\033[0m'
            printer(out_str)
    else:
        for v in print_list:
            out_str = f' [ \033[{sm};{fc};{bc}m{v}\033[0m ]'
            printer(out_str)
    printer(end_out)
    time.sleep(0.4)


def printer(note, log_lever='info', interactive_mode=False):
    if interactive_mode:
        sys.stdout.write(note)
        sys.stdout.write('\n')
    else:
        if log_lever == 'info':
            LOGGER.info(note)
        elif log_lever == 'warn':
            LOGGER.warning(note)
        elif log_lever == 'error':
            LOGGER.error(note)
        else:
            LOGGER.debug(note)
