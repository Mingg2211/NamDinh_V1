import pandas as pd
from itertools import chain
import regex as re
from underthesea import word_tokenize
from src.core.api.config import * 

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

def ranking_result(user_sent:str):
    values_dict = load_dict_values(DATA_TXT)
    best_matching = find_best_matching_in_dict(user_sent, values_dict)
    user_tokens = word_tokenize(user_sent)
    tmp =[]
    for token in user_tokens:
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
        return unique_list[:5]
    elif len(dup_list) <5 :
        n = 5 - len(dup_list)
        if best_matching:
            result = [best_matching] + dup_list + unique_list[:10]
            result = remove_dup(result)
            return result[:5]
        else :
            result = dup_list + unique_list[:5-n]
            return result[:5]
    else:
        if best_matching in dup_list:
            result = [best_matching] + dup_list
            result = remove_dup(result)
            return result[:5]
        else:
            return dup_list[:5]