import argparse
import logging
import os
import re
from collections import Counter
from multiprocessing import cpu_count
from multiprocessing.pool import Pool

from duplremover.resourse_and_gears import note_printer, printer


class DuplRm(object):

    def __init__(self,
                 directory,
                 recursive_traversal=True,
                 types=None,
                 sampling_matching=True,
                 interactive_mode=False,
                 auto_delete=False,
                 remove_zero_size_file=False,
                 remove_empty_dirs=False,
                 multiprocess=False,
                 log_level=None,
                 ):
        """
        :param directory: 需要检查的根目录
        :param recursive_traversal: 是否递归遍历，若False则只检查前面指定的目录下的文件，而不检查任何子目录
        :param types: 指定需要检查的文件类型，列表的形式传入多个具体文件后缀，例如 ['jpg', 'png']，大小写不敏感
        :param log_level: 指定输出的log的级别
        :param interactive_mode: 是否以交互模式运行
        :param auto_delete: 是否自动清理重复项
        :param remove_zero_size_file: 是否自动清理0大小的文件
        :param remove_empty_dirs: 是否自动清理空文件夹
        :param multiprocess: 是否使用多进程完成任务，注意若使用多进程则输出日志可能错乱
        :param sampling_matching: 是否以文件二进制抽样的方式去重，当待去重的文件之间的区别较小的时候（例如超高速连拍的照片），
                        建议设置为False，否则在抽样时很可能错过这些微小的差别。
        """
        super(DuplRm, self).__init__()
        self.INTERACTIVE_MODE = interactive_mode
        self.SAMPLE_MATCH = sampling_matching
        self.AUTO_DELETE = auto_delete
        self.RM_ZERO = remove_zero_size_file
        self.MULTIPROCESS = multiprocess
        self.RM_EM_DIR = remove_empty_dirs
        self.dir = directory
        self.rt = recursive_traversal
        self.RM_COUNT = 0

        self.PHOTO_TYPES = {
            'photo',
            'photos',
            'pic',
            'picture',
            'pics',
            'pictures',
            'img',
            'imgs',
            'image',
            'images'
        }
        self.VIDEO_TYPES = {
            'video',
            'videos',
            'movie',
            'movies',
        }

        self.PHOTO_FILE_SUFFIX = {
            'jpg',
            'jpeg',
            'png',
            'gif',
            'bmp'
        }
        self.VIDEO_FILE_SUFFIX = {
            'avi',
            'wmv',
            'rm',
            'rmvb',
            'mpeg1',
            'mpeg2',
            'mpeg4',
            'mp4',
            '3gp',
            'asf',
            'swf',
            'vob',
            'dat',
            'mov',
            'm4v',
            'flv',
            'f4v',
            'mkv',
            'mts',
            'ts',
            'imv',
            'amv',
            'xv',
            'qsv'
        }

        types = self._check_types(types)
        self.TYPE_FILTER = types

    def start(self):
        if not os.path.isdir(self.dir):
            raise ValueError('Your directory input does not look right, please check and re-enter')
        files_lis = [os.path.join(root, n) for root, dirs, files in os.walk(self.dir, topdown=False) for n in files]
        files_suffixes_raw = [x.split('.')[-1] for x in files_lis]
        files_lis_counted = Counter(files_suffixes_raw)
        files_paths = [x for x in files_lis if files_lis_counted.get(x.split('.')[-1], 0) > 1]
        files_suffixes = [x.split('.')[-1] for x in files_paths]
        files_count = ["{} : {}".format(k, v) for k, v in
                       sorted(list(Counter(files_suffixes).items()), key=lambda x: x[-1], reverse=True)]
        total_str_out = 'total files: {}'.format(len(files_suffixes))
        if self.INTERACTIVE_MODE and self.TYPE_FILTER == 'all':
            top_note = 'select the nums of the suffix that you want to check duplicate bellow'
            note_printer(files_count, top_note=top_note, end_note='end', front_color="yellow")
            input_str = ' your selection(input like this: 1,3,4; empty to select all):  '
            user_selection = self._check_input(input(input_str), list(range(len(files_count))))
            suffixes_selected = [files_count[x].split(':')[0].strip() for x in user_selection] if user_selection \
                else [x.split(':')[0].strip() for x in files_count]
            suffixes_selected_set = set(suffixes_selected)
        else:
            printer(total_str_out, interactive_mode=self.INTERACTIVE_MODE)
            suffixes_selected = [x.split(':')[0].strip() for x in files_count] if self.TYPE_FILTER == 'all' else \
                [x.split(':')[0].strip() for x in files_count if x.split(':')[0].strip().lower() in self.TYPE_FILTER]
            suffixes_selected_set = set(suffixes_selected)
            files_count_lis = [x for x in files_count if x.split(':')[0].strip() in suffixes_selected_set]
            fc_tn = 'all types in this dir'
            note_printer(files_count_lis, top_note=fc_tn, end_note='end', fill_str='-', disordered_mode=True, front_color="yellow")

        printer('start to process', interactive_mode=self.INTERACTIVE_MODE)
        selected_paths = [x for x in files_paths if x.split('.')[-1] in suffixes_selected_set]
        selected_paths_dic = dict()
        for f_path in selected_paths:
            f_suffix = f_path.split('.')[-1].lower()
            if selected_paths_dic.get(f_suffix):
                selected_paths_dic[f_suffix].append(f_path)
            else:
                selected_paths_dic[f_suffix] = [f_path]

        return_dict = {}

        if self.MULTIPROCESS:
            selected_lis = [fp_lis for s_type, fp_lis in selected_paths_dic.items()]
            pool = Pool(cpu_count())
            duplicated_list = pool.map(self._check_duplicate, selected_lis)
            pool.close()
            pool.join()
            dump = [return_dict.update({lis[0].split('.')[-1]: lis}) for lis in duplicated_list if lis]
            del dump
        else:
            for suffix_type, file_path_lis in selected_paths_dic.items():
                dp_paths = self._check_duplicate(file_path_lis)
                if dp_paths:
                    return_dict[suffix_type] = dp_paths

        if self.RM_EM_DIR and self.AUTO_DELETE:
            em_dirs = [os.path.join(root, n) for root, dirs, files in os.walk(self.dir, topdown=False) for n in dirs]
            for i in em_dirs:
                try:
                    os.removedirs(i)
                except:
                    pass

        if return_dict:
            for the_type, dp_lis in return_dict.items():
                tn = f'[ {the_type} ] duplicate files'
                note_printer(dp_lis, top_note=tn, fill_str='-', disordered_mode=True, front_color="red")
            return return_dict

    def _check_duplicate(self, files_path_list):
        suffix_type = files_path_list[0].split('.')[-1]
        printer(f'processing type [ \033[0;32;48m{suffix_type}\033[0m ]', interactive_mode=self.INTERACTIVE_MODE)
        new_list = []
        path_id_dict = {}
        for f_path in files_path_list:
            file_id = self._get_file_sample(f_path, return_type='int')
            if file_id:
                path_id_dict[f_path] = file_id
            else:
                if self.RM_ZERO:
                    os.remove(f_path)
                    self.RM_COUNT += 1
                    printer(f'found and deleted: Zero size file :\n {f_path}', interactive_mode=self.INTERACTIVE_MODE)
        id_path_lis_dic = {}
        for path, f_id in path_id_dict.items():
            if f_id in id_path_lis_dic:
                id_path_lis_dic[f_id].append(path)
            else:
                id_path_lis_dic[f_id] = [path]
        id_path_lis_dic = {f_id: ps for f_id, ps in id_path_lis_dic.items() if len(ps) > 1}
        duplicated_found = False
        for i, ps in id_path_lis_dic.items():
            ps = sorted(ps, key=lambda x: len(x), reverse=True)
            duplicated_found = True
            if self.AUTO_DELETE:
                new_list.append(ps.pop(-1))
                sl = self._files_remover(ps, return_count=False, return_lis=True)
                printer('auto deleted: \n{}\n'.format("\n".join(sl)), interactive_mode=self.INTERACTIVE_MODE)
            elif not self.AUTO_DELETE and self.INTERACTIVE_MODE:
                note_printer(ps, top_note='Duplicate files detected', end_note='end', front_color="red")
                ip_str = 'Choose the options you need to keep(input like "0" or "0,1"; empty to keep all): '
                user_selection = self._check_input(input(ip_str), list(range(len(ps))))
                selection_set = set(user_selection)
                rm_lis = [ps[i] for i, _ in enumerate(ps) if i not in selection_set] if selection_set else []
                if rm_lis:
                    tn = 'the following files will be remove'
                    note_printer(rm_lis, top_note=tn, fill_str='~', disordered_mode=True, front_color="red", show_mode="blinking")
                    confirm = input(' >>> please confirm(yes?): ')
                    if confirm.strip().lower() == 'yes' or confirm.strip().lower() == 'y':
                        sc_str = self._files_remover(rm_lis)
                        printer(f'  {sc_str} files has been delete', interactive_mode=self.INTERACTIVE_MODE)
                    else:
                        printer('cancel deletion', interactive_mode=self.INTERACTIVE_MODE)
                else:
                    pass
            else:
                # printer('Duplicate files detected, will return as a dict and without delete any of them', interactive_mode=self.INTERACTIVE_MODE)
                return ps
        if not duplicated_found:
            printer('No duplicates found in this type', interactive_mode=self.INTERACTIVE_MODE)

    def _files_remover(self, f_lis, return_count=True, return_lis=False):
        success_count = 0
        success_lis = []
        for f in f_lis:
            try:
                os.remove(f)
                self.RM_COUNT += 1
                success_count += 1
                success_lis.append(f)
            except PermissionError:
                printer(f'Permission Error! can not delete "{f}"', interactive_mode=self.INTERACTIVE_MODE)
                continue
        count_str = "{}/{}".format(success_count, len(f_lis))
        if return_count and not return_lis:
            return count_str
        elif return_count and return_lis:
            return count_str, success_lis
        elif not return_count and return_lis:
            return success_lis
        else:
            pass

    def _get_file_sample(self, f_path, n=20, return_type='list'):
        lis = []
        s = os.path.getsize(f_path)
        if s > 0:
            try:
                rf = open(f_path, 'rb')
            except PermissionError:
                printer(f'Permission Error! can not read file: {f_path}', interactive_mode=self.INTERACTIVE_MODE)
                return
            if 0 < s <= 100 or not self.SAMPLE_MATCH:
                dump = [lis.append(x) for x in rf.read()]
                del dump
            else:
                for i in range(0, s, s // n):
                    rf.seek(i)
                    byte_int = int.from_bytes(rf.read(1), 'little')
                    lis.append(byte_int)
            rf.close()
            if return_type == 'list':
                return lis
            elif return_type == 'int':
                return int(''.join([str(x) if x else '' for x in lis]))
            else:
                return ''.join([str(x) if x else '' for x in lis])

    def end(self):
        printer(note='process done !', interactive_mode=self.INTERACTIVE_MODE)
        if self.RM_COUNT:
            note = f'total delete {self.RM_COUNT} files'
            printer(note, interactive_mode=self.INTERACTIVE_MODE)

    @staticmethod
    def _check_input(raw_inputs, raw_nums=None):
        temp_inputs = re.findall(r'(\d+)', raw_inputs) if raw_inputs else ''
        inputs = [int(x) for x in temp_inputs] if temp_inputs else []
        inputs = list(set(inputs))
        inputs.sort()
        raw_nums = set(raw_nums) if raw_nums is not None else set()
        inputs = [x for x in inputs if x in raw_nums] if raw_nums else inputs
        return inputs

    def _check_types(self, raw_types):
        types = 'all'
        if isinstance(raw_types, list) or isinstance(raw_types, set) or isinstance(raw_types, tuple):
            if all([True if isinstance(x, str) else False for x in raw_types]):
                types = set(raw_types)
            else:
                error_types = ', '.join([self._type_str(r) for r in raw_types])
                printer('param types error, {}'.format(error_types))
                raise ValueError('types expect string in list, not {}'.format(error_types))
        elif isinstance(raw_types, str):
            raw_types = raw_types.lower()
            if raw_types in self.PHOTO_TYPES:
                types = self.PHOTO_FILE_SUFFIX
            elif raw_types in self.VIDEO_TYPES:
                types = self.VIDEO_FILE_SUFFIX
        return types

    @staticmethod
    def _type_str(val):
        return re.findall(r"class '([^']+?)'", str(type(val)))[0]


def format_args(arg, default=False):
    return True if arg and arg.lower() == 'y' or arg is None else default


def rmduplicate(args=None):
    dp = ' *** 这是一个删除重复文件数据（不管文件名是否一样）的小工具'
    da = "--->   "
    parser = argparse.ArgumentParser(description=dp, add_help=True)
    parser.add_argument("-f", "--folder", type=str, dest="folder",
                        default='', help=f'{da}需要查找的文件夹，默认运行目录')
    parser.add_argument("-t", "--types", type=str, dest="types",
                        default='**-all-**', help=f'{da}y/n 需要检查的文件后缀的列表，使用英文逗号隔开(不要有空格)，例如：jpg,png')
    parser.add_argument("-i", "--interactive_mode", type=str, dest="interactive_mode",
                        nargs='?', default='n', help=f'{da}交互模式，即找到重复文件就进行询问')
    parser.add_argument("-a", "--auto_delete", type=str, dest="auto_delete",
                        nargs='?', default='n', help=f'{da}y/n 是否自动删除找到的重复文件')
    parser.add_argument("-rf", "--remove_zero_size_file", type=str, dest="remove_zero_size_file",
                        nargs='?', default="n", help=f'{da}y/n 是否删除空文件，请注意，很多空文件是有用的，例如 __init__.py')
    parser.add_argument("-rd", "--remove_empty_dirs", type=str, dest="remove_empty_dirs",
                        nargs='?', default="n", help=f'{da}y/n 是否删除空文件夹')
    parser.add_argument("-nsm", "--not_sampling_matching", type=str, dest="not_sampling_matching",
                        nargs='?', default="n", help=f'{da}y/n 是否不以取样方式匹配文件，若文件不大，且重复可能性高，建议开启此项')
    parser.add_argument("-mp", "--multiprocess", type=str, dest="multiprocess",
                        nargs='?', default="n", help=f'{da}y/n 是否开启多进程处理，注意，开启后可能导致输出日志显示不正常')
    args = parser.parse_args()

    folder = args.folder
    types = args.types

    interactive_mode = format_args(args.interactive_mode)
    auto_delete = format_args(args.auto_delete)
    remove_zero_size_file = format_args(args.remove_zero_size_file)
    remove_empty_dirs = format_args(args.remove_empty_dirs)
    not_sampling_matching = format_args(args.not_sampling_matching)
    multiprocess = format_args(args.multiprocess)

    if not folder:
        folder = os.getcwd()

    if types == "**-all-**":
        types = None
    else:
        types = [x.strip() for x in types.split(',') if x.strip()]
        types = types if types else None

    dp = DuplRm(directory=folder,
                interactive_mode=interactive_mode,
                auto_delete=auto_delete,
                types=types,
                remove_zero_size_file=remove_zero_size_file,
                remove_empty_dirs=remove_empty_dirs,
                sampling_matching=not_sampling_matching,
                multiprocess=multiprocess
                )
    try:
        dp.start()
    except KeyboardInterrupt:
        dp.end()


if __name__ == '__main__':
    rmduplicate()
