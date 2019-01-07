import re
import numpy as np  # 有时用来判断列表维度，若无该库，请把 assert np.array(list).ndim == num 注释！


def split_sentence(cont):
    """
    a good way to split sentence. what's more, it can retain punctuations.

    :param cont: string, text which may contain many sentences
    :return: 1d list, a list of sentences which are from text
    """

    assert isinstance(cont, str)

    re_sen = re.compile('([。！？\.!?]+)')  # 用来分割句子的符号
    sentence_list = []
    tmp_list = re_sen.split(cont)
    tmp_str = ''
    length = len(tmp_list)

    for i in range(length):
        if tmp_list[i]:  # assert
            if not re_sen.search(tmp_list[i]):
                tmp_str = tmp_list[i]
                if i == length-1:  # the last element
                    sentence_list.append(tmp_str)  # 最后一部分没有断句符号也要当作一个句子

            else:
                tmp_str += tmp_list[i]
                sentence_list.append(tmp_str)
                tmp_str = ''

    return sentence_list


def sentence_to_article(input_list):
    """
    merge from several sentences to one article according to theirs attributes

    :param input_list: 2d list, consists of sentence and at least one attribute
    :return: 1d list, consists of those articles
    """

    assert np.array(input_list).ndim == 2

    length = len(input_list)
    article_list = []
    tmp_list = []
    tmp_att = ''

    for i in range(length):
        sentence = input_list[i][0]
        attribute = input_list[i][1]  # fixed temporarily
        if tmp_att != attribute:
            if tmp_list:
                article_list.append('\n'.join(tmp_list))
                tmp_list = [sentence]
            else:  # tmp_list is empty only when i == 0
                tmp_list.append(sentence)

            tmp_att = attribute  # update

        else:
            tmp_list.append(sentence)

        if i == length - 1:
            article_list.append('\n'.join(tmp_list))

    return article_list


def get_position(cont, ch):
    """
    get the position of a character in a string content

    :param cont: string, input string
    :param ch: string, a character or a word
    :return: 2d list, consists of elements of position
    """

    assert isinstance(cont, str)
    assert isinstance(ch, str)

    begin = 0
    size = len(cont)
    length = len(ch)
    pos_list = []

    while begin < size:
        pos = cont.find(ch, begin, size)
        if pos == -1:
            break

        else:
            pos_list.append((pos, pos + length))
            begin = pos + length

    return pos_list


def clean_text(cont, degree='Normal'):
    """
    清洗文本，去html标签及无用符号

    :param cont: string, original text
    :param degree: string, denote the extent of this processing, including Normal, Deeper and NoPackage
    :return: string, new text without html labels or useless signs
    """

    assert isinstance(cont, str)

    text = re.sub('<[^<>]*>', '', cont)
    if degree in ['Deeper', 'NoPackage']:
        text = re.sub('<![\S]CDATA[\S]|]]>', '', text)  # 去掉CDATA封装，保留标签内容
        text = re.sub('<!--|-->', '', text)  # 去掉注释标签，保留标签内容（规整的注释标签无需使用）

        if degree == 'Deeper':
            import html2text
            text_maker = html2text.HTML2Text()
            text_maker.ignore_links = True
            text_maker.ignore_images = True
            text_maker.ignore_tables = True
            text = text_maker.handle(text)
            text = re.sub('&#?\w+;', '', text)  # 去特殊无用字符

    else:
        if degree != 'Normal':
            print('warning: invalid degree, execute Normal')

    return text.strip()


def remove_empty(input_list, category='Both'):
    """
    remove empty element

    :param input_list: list, consists of elements which may be empty
    :param category: string, denote the requirements, including All, Both, Left, Right
    :return: list
    """

    assert isinstance(input_list, list)

    if category == 'All':  # all empty elements
        return [tmp for tmp in input_list if tmp]

    else:
        if not input_list:
            return []

        else:
            begin = 0
            end = len(input_list)
            for i in range(len(input_list)):
                if input_list[i]:
                    begin = i
                    break

            for i in range(len(input_list)-1, -1, -1):
                if input_list[i]:
                    end = i + 1
                    break

            if category == 'Both':  # both direction
                return input_list[begin:end]

            elif category == 'Left':
                return input_list[begin:]

            elif category == 'Right':
                return input_list[:end]

            else:
                print('warning: invalid category')
                return []


def de_weight_list(input_list, seq_flag=True):
    """
    列表信息去重

    :param input_list: 1d list, consists of string content
    :param seq_flag: bool, denote whether retain sequence of this list or not
    :return: 1d list, consists of string content after de-weight
    """

    assert np.array(input_list).ndim == 1

    if not seq_flag:
        return list(set(input_list))

    else:  # 保持列表先后顺序的去重
        result = []
        tmp_coll = set([])
        for tmp in input_list:
            if tmp not in tmp_coll:  # O(1)
                tmp_coll.add(tmp)
                result.append(tmp)

        return result


def pack_list(input_list, pack_size=5000):
    """
    列表片段打包

    :param input_list: 1d list, the whole list
    :param pack_size: int, the number of a pack
    :return: 2d list  [pack_list, pack_list]
    """

    assert np.array(input_list).ndim == 1

    length = len(input_list)
    k = 0
    result = []
    while pack_size*k < length:
        result.append(input_list[pack_size*k:pack_size*(k+1)])  # 注意：最后一次下标溢出但无问题!
        k += 1

    return result


def occur_by_probability(prob_pair_list, filter_list=[]):
    """
    通过指定的概率生成相应的词语

    :param prob_pair_list: 2d list, it consists of words and their probabilities   [(word, possibility),]
    :param filter_list: 1d list, it consists of words which are not expected
    :return: string, an eligible word
    """

    assert np.array(prob_pair_list).ndim == 2
    assert np.array(filter_list).ndim == 1  # attention the dim value of np.array([]) is also 1

    import random
    result = None
    sum_prob = sum([float(elem[1]) for elem in prob_pair_list])
    if round(abs(sum_prob-1.0), 2) > 0.01:  # 保证列表中元素相加为1,但设置一个误差
        return result  # 有错误则返回None

    filter_coll = set(filter_list)
    length = len(prob_pair_list)
    begin = 0
    tmp_list = []

    for i in range(length):
        end = begin + int(100 * float(prob_pair_list[i][1]))
        tmp_list.append((begin, end))
        begin = end

    while 1:
        num = random.randint(1, 100)
        for i in range(length):
            if tmp_list[i][0] < num <= tmp_list[i][1]:
                result = prob_pair_list[i][0]
                break

        if result not in filter_coll:
            break

    return result  # 正确则返回选取的那个词


def rank_words(input_list, rev_flag=True):
    """
    统计并排序

    :param input_list: 1d list or 2d list, we can extract words and their frequencies from input_list
    :param rev_flag: bool, denote whether to sort elements in the word-freq list by reverse
    :return: 1d list, final sorted word-freq list
    """

    assert isinstance(input_list, list)

    sta_dic = {}
    tmp_list = []
    try:
        if np.array(input_list).ndim == 2:  # 二维列表
            for i in range(len(input_list)):
                tmp_list.extend(input_list[i])  # 二维列表转一维列表
        else:
            tmp_list = input_list

    except Exception as err:
        print(err)
        return []

    for t in tmp_list:
        if t not in sta_dic:
            sta_dic[t] = 1
        else:
            sta_dic[t] += 1

    result = sorted(sta_dic.items(), key=lambda e: e[1], reverse=rev_flag)

    return result


def string_distance(str_a, str_b):
    """
    两字符串的距离的定义为从前一个字符串通过删除、添加和替换操作需要多少次操作能够变成后一个字符串
    两字符串的距离越大，可认为二者相似度越小
    注意: 两个字符串的编辑距离肯定不超过它们的最大长度
    dp_table[i][j] 表示 str_a 的前i个字符变为 str_b 的前j个字符所需要的最小步骤数, 这里 i,j 均从 1 开始
    当 str_a[i] == str_b[j] 时, 无需操作了, dp_table[i][j] == dp_table[i-1][j-1]
    当 str_a[i] != str_b[j] 时,dp_table[i][j] = dp_table[i-1][j]+1 表示 str_a 删除了它最后的字符,
    dp_table[i][j] = dp_table[i][j-1]+1 表示 str_a 插入了 str_b 最后的字符,
    dp_table[i][j] = dp_table[i-1][j-1]+1 表示 str_a 最后的字符 替换成了 str_b 最后的字符
    """
    if not str_a or not str_b:  # 无需动态规划即可得出
        return max(len(str_a), len(str_b))

    a = len(str_a) + 1
    b = len(str_b) + 1
    dp_table = [[0 for __ in range(b)] for _ in range(a)]

    # 因为迭代中有 i-1 和 j-1，先求 dp_table[0][j] 和 dp_table[i][0]
    for i in range(1, a):
        dp_table[i][0] = dp_table[i-1][0] + 1

    for j in range(1, b):
        dp_table[0][j] = dp_table[0][j-1] + 1

    for i in range(1, a):
        ch_a = str_a[i-1]
        for j in range(1, b):
            ch_b = str_b[j-1]
            if ch_a == ch_b:
                dp_table[i][j] = dp_table[i-1][j-1]
            else:
                val1 = dp_table[i-1][j] + 1  # delete
                val2 = dp_table[i][j-1] + 1  # insert
                val3 = dp_table[i-1][j-1] + 1  # substitute

                dp_table[i][j] = min(val1, val2, val3)

    return dp_table[-1][-1]


if __name__ == '__main__':
    '''
    partial test   
    '''
    text = '我非常喜欢算法！I am very interested in algorithm.特别是NLP'
    print(split_sentence(text))


    input_list = [('hello world', '1'), ('really', '1'), ('please close the door', '2'), ('end', '2')]
    print(sentence_to_article(input_list))


    input_list = ['', '', [], 'today', [], 'is', '', [], 'Monday', '', []]
    print(remove_empty(input_list, 'All'))
    print(remove_empty(input_list, 'Both'))


    prob_pair_list = [('清华', 0.28), ('北大', 0.28), ('复旦', 0.2), ('上交', 0.19), ('other', 0.05)]
    print(occur_by_probability(prob_pair_list, filter_list=['清华', '北大']))


    str_a = 'ramble'
    str_b = 'rab'
    print(string_distance(str_a, str_b))





