import pandas as pd
from itertools import chain
import regex as re
from underthesea import word_tokenize
from src.core.api.config import *


def look_up_in_domain(token):
    look_up_dict = {"ô tô":["ô tô","oto"],
                    "kết hôn":["kết hôn","cưới","cưới xin","lấy vợ lấy chồng","kết duyên","thành hôn","thành thân",'cưới vợ','cưới chồng'],
                    "photocopy":["photocopy","photo"],
                    "di dời":["di dời","dời đi"],
                    "huy chương":["huy chương","huân chương"],
                    "toàn bộ":["toàn bộ","tất cả"],
                    "đăng ký kết hôn":["đăng ký kết hôn","đăng ký hôn nhân"," đăng ký cưới xin"," đăng ký cưới"," đăng kí cưới"," đăng kí cưới xin"," đăng ký hôn nhân"],
                    "du học":["du học","học nước ngoài"," đi  học nước ngoài"],
                    "thuế":["thuế","thuế má"],
                    "thức ăn":["thức ăn","đồ ăn"],
                    "con đẻ":["con đẻ","con ruột"],
                    "bất động sản":["bất động sản","địa ốc"],
                    "thương lượng":["thương lượng","đàm phán"],
                    "chặt hạ":["chặt hạ","đốn hạ"],
                    "luồng lạch":["luồng lạch","luồn lách"],
                    "cơ sở vật chất":["cơ sở vật chất","csvc"],
                    "khoa học xã hội":["khoa học xã hội","khxh"],
                    "công khai":["công khai","công bố"],
                    "hôn nhân":["hôn nhân","hôn lễ"],
                    "hoãn":["hoãn","trì hoãn"],
                    "nhà đất":["nhà đất","nhà ở và đất đai"],
                    "tiền lương":["tiền lương","lương"],
                    "đầu tư sản xuất":["đầu tư sản xuất","đầu tư sx"],
                    "chứng khoán":["chứng khoán","chung khoan"],
                    "nông lâm":["nông lâm","lâm nông"],
                    "lao động-thương binh":["lao động-thương binh","lđtb"],
                    "an toàn lao động":["an toàn lao động","atlđ"],
                    "trực tuyến":["trực tuyến","online"],
                    "tố tụng":["tố tụng","tố"],
                    "khiêu vũ":["khiêu vũ","nhảy"],
                    "nâng cấp":["nâng cấp","cải tiến"]}
    # count = 0
    if (token):
        for key in look_up_dict.keys():
            if token in look_up_dict[key]:
                return key
        return token
    else:
        return token

def load_dict_values(dict_file):
    fin = open(dict_file, 'r', encoding='utf-8')
    lines = fin.readlines()
    fin.close()
    values_dict = []
    for line in lines:
        # print('line : ', line)
        items = line.strip().split('\t')
        # print('items : ', items)
        if len(items) == 2:
            words = items[0].lower().split()
            values_dict.append((words, items[1]))
    return values_dict


def lcs(X, Y):
    # find the length of the strings
    m = len(X)
    n = len(Y)

    # declaring the array for storing the dp values
    L = [[None] * (n + 1) for i in range(m + 1)]

    """Following steps build L[m + 1][n + 1] in bottom up fashion
    Note: L[i][j] contains length of LCS of X[0..i-1]
    and Y[0..j-1]"""
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif X[i - 1] == Y[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])

    return L[m][n]


def find_best_matching_in_dict(query, values_dict):
    query_words = query.lower().split()
    max_ratio = 0
    str_found = ""
    for words, v in values_dict:
        r = 1.0 * lcs(words, query_words) / len(words)
        if r > max_ratio:
            max_ratio = r
            str_found = v
    return str_found


def remove_dup(result_list):
    return list(dict.fromkeys(result_list))

def search_in_database(user_token):
    df = pd.read_csv(DATA_CSV)
    procedures = df[df.procedure_name.str.contains(user_token, na=False)]
    # flatten 2d list
    procedure_list = list(chain.from_iterable(procedures.values.tolist()))
    procedure_list = sorted(procedure_list, key=len)
    return procedure_list

def ranking_result(user_sent: str):
    values_dict = load_dict_values(DATA_TXT)
    user_tokens = word_tokenize(user_sent)
    new_user_token = []
    for item in user_tokens:
        new_user_token.append(look_up_in_domain(item))
    best_matching = find_best_matching_in_dict(user_sent, values_dict).capitalize()
    tmp = []
    for token in new_user_token:
        tmp += search_in_database(token)
    unique_list = []
    dup_list = []
    for element in tmp:
        if element not in unique_list:
            unique_list.append(element)
        else:
            dup_list.append(element)
    dup_list = remove_dup(dup_list)
    for element in dup_list:
        if element in unique_list:
            unique_list.remove(element)
    if len(dup_list) == 0:
        return unique_list[:3]
    elif len(dup_list) < 3:
        n = 3 - len(dup_list)
        if best_matching:
            result = [best_matching] + dup_list + unique_list[:10]
            result = remove_dup(result)
            return result[:3]
        else:
            result = dup_list + unique_list[:3-n]
            return result[:3]
    else:
        if best_matching in dup_list:
            result = [best_matching] + dup_list
            result = remove_dup(result)
            return result[:3]
        else:
            return dup_list[:3]
