import os
import re
import sqlite3
import sys
from datetime import datetime

import chardet

from app.common.log import logs


class linkError(Exception):
    ...


def get_txt_files(root_dirs):
    '''遍历指定目录列表下txt 返回绝对路径'''
    txt_files = []
    for root_dir in root_dirs:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith('.txt'):
                    txt_files.append(
                        os.path.join(
                            dirpath,
                            filename).replace(
                            '\\',
                            '/'))

    return txt_files


def convert_bytes(num_bytes: int, standard=1000) -> str:
    '''字节转换为Mb或Gb'''
    mb = num_bytes / 1024 ** 2
    if mb < standard:
        return f"{mb:.2f} MB"
    else:
        gb = num_bytes / 1024 ** 3
        return f"{gb:.2f} GB"


def decode_ed2k(ed2ks: list, path: str = '') -> list:
    """ 
    分析ed2k 返回 ed2k信息       

    ed2k://|file|1.rar|52662259397|0A5556F2D7C04702E420D3B586274FC1|/

    Parameters
    ----------
    ed2ks : list
        ed2k 链接列表
    path : str, optional
        文件路径, by default ''

    Returns
    -------
    list
        返回列表 每一个元素都是包含对应ed2k信息
        {
        'filename'
        'extension'
        'size_byte'
        'size'
        'hash'
        'link'
        'path'
        'time'
        }

    """

    ed2k_infos = []
    ed2k_infos_list = []
    p = re.compile(r'ed2k://\|file\|(.*)\.(.*)\|(.*)\|(.*)\|/')

    for ed2k in ed2ks:
        n = ed2k.count('|')
        if n == 6:
            p = re.compile(r'ed2k://\|file\|(.*)\.(.*)\|(.*)\|(.*)\|(.*)\|')
        elif n != 5:
            print(123)
            logs.debug(f'检测到无法识别的链接：{ed2k}，跳过')
            continue

        match = p.search(ed2k)

        if match:
            one = match.groups()
            time_now = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")

            ed2k_info = {'filename': one[0], 'extension': one[1], 'size_byte': one[2],
                         'size': convert_bytes(int(one[2])), 'hash': one[3],
                         'link': ed2k, 'path': path, 'time': time_now}
            ed2k_infos.append(ed2k_info)

            ed2k_info_values = list(ed2k_info.values())
            ed2k_infos_list.append(ed2k_info_values)

    return ed2k_infos, ed2k_infos_list


def detect_file_encoding(file_path: str) -> str:
    """返回文件编码"""
    with open(file_path, 'rb') as f:
        rawdata = f.read()

    return chardet.detect(rawdata)['encoding']


def txt_to_ed2k_info_list(filepath: str):
    encode = detect_file_encoding(filepath)

    with open(filepath, 'r', encoding=encode) as f:
        ed2k_list = [line.strip()
                     for line in f if line.strip() and 'ed2k' in line]

        ed2k_infos, ed2k_infos_list = decode_ed2k(ed2k_list, path=filepath)

        return ed2k_infos, ed2k_infos_list


def ed2k_infos_to_db(ed2k_infos: list,
                     database_path: str = os.path.join(os.path.dirname(sys.argv[0]), 'data/database.db'),
                     table_name: str = 'temp', init_delete: bool = True, deduplicate=False):
    conn = sqlite3.connect(database_path)
    c = conn.cursor()

    if init_delete:
        c.execute(f"DELETE FROM {table_name}")

    columns = ', '.join(ed2k_infos[0].keys())
    placeholders = ':' + ', :'.join(ed2k_infos[0].keys())
    query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'

    c.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} ({columns})''')

    c.executemany(query, ed2k_infos)

    if deduplicate:
        c.execute(
            f'DELETE FROM {table_name} WHERE rowid NOT IN (SELECT MAX(rowid) FROM {table_name} GROUP BY hash)')

    conn.commit()
    conn.close()


# def ed2k_link_txt_to_database(filepath: str, database_path: str = 'data/database.db', table_name: str = 'temp', init_delete: bool = True, to_db: str = True) -> None:
#     """txt文件ed2k 存入db中


#     """
#     encode = detect_file_encoding(filepath)

#     with open(filepath, 'r', encoding=encode) as f:
#         ed2k_list = [line.strip()
#                      for line in f if line.strip() and 'ed2k' in line]

#         ed2k_infos = decode_ed2k(ed2k_list, path=filepath)

#     if not to_db:
#         return ed2k_infos

#     conn = sqlite3.connect(database_path)
#     c = conn.cursor()

#     # c.execute(f'''CREATE TABLE IF NOT EXISTS {table_name}
#     #          (filename,extension,size_byte,size,hash,link,path,time)''')

#     if init_delete:
#         c.execute(f"DELETE FROM {table_name}")

#     columns = ', '.join(ed2k_infos[0].keys())
#     placeholders = ':'+', :'.join(ed2k_infos[0].keys())
#     query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'

#     c.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} ({columns})''')

#     c.executemany(query, ed2k_infos)

#     # for ed2k_info in ed2k_infos:
#     #     c.execute(f'INSERT INTO {table_name} VALUES (?,?,?,?,?,?,?,?)',
#     #               (ed2k_info['filename'], ed2k_info['extension'], ed2k_info['size_byte'],  ed2k_info[
#     #                   'size'], ed2k_info['hash'], ed2k_info['link'], ed2k_info['path'],
#     #                ed2k_info['time']))

#     conn.commit()
#     c.execute("VACUUM")
#     conn.close()


def read_db_to_list(database_path: str = os.path.join(os.path.dirname(sys.argv[0]), 'data/database.db'),
                    table_name: str = 'temp') -> list:
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute(f'SELECT filename,extension,size,path FROM {table_name}')
    data = c.fetchall()

    conn.commit()
    c.execute("VACUUM")
    conn.close()

    data = [list(row) for row in data]

    return data
