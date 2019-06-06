# -*- coding: utf-8 -*-

def to_milion(num, u=1000000):
    num = int(num)
    if num % u == 0:
        num = int(num/u)
    else:
        num = round(float(num/u), 1)
        
    return '{}'.format(num)

def join_by_slag(first='-', second='-'):
    if type(first) != 'str':
        first = str(first)
    if type(second) != 'str':
        second = str(second)
        
    return first + '/' + second

def add_comma(num):
    return format(int(num), "8,d")

def add_comma_float(num):
    return format(float(num), "8,.1f")

def number_colored(num, tag='span', color='#9900ff'):
    return '<%s style="color:%s;">%s</%s>' % (tag, color, str(num), tag)

def sortkeypicker(keynames):
    negate = set()
    for i, k in enumerate(keynames):
        if k[:1] == '-':
            keynames[i] = k[1:]
            negate.add(k[1:])
    def getit(adict):
       composite = [adict[k] for k in keynames]
       for i, (k, v) in enumerate(zip(keynames, composite)):
           if k in negate:
               composite[i] = -v
       return composite
    return getit

def make_beauti(num):
    if isinstance(num, float):
        return num
    
    try:
        num = int(num)
    except:
        num = 0
    return num

def custom_extend(first_list, second_list):
    res = []
    if len(first_list) == 0:
        first_list = [0]*len(second_list)
    min_len = min(len(first_list), len(second_list))
    for i in range(0, min_len):
        if "/" in str(second_list[i]):
            if "/" in str(first_list):
                tmp_first = str(first_list[i]).split('/')
            else:
                tmp_first = [0, 0]
            tmp_second = list(map(make_beauti, str(second_list[i]).split('/')))
            tmp_val = [make_beauti(x) + make_beauti(y) for x, y in zip(tmp_first, tmp_second)]
            val_to_append = "/".join(map(str, tmp_val))
            res.append(val_to_append)
        else:
            res.append(first_list[i] + make_beauti(second_list[i]))
    return res

def decorate_report_content(report_content):
    import re
    
    raw_report_content = report_content
    
    
    # for number / number
    complex_number = re.findall(r'>\d+/\d+<', raw_report_content)
    for tmp in complex_number:
        first = re.findall(r'\d+/', tmp)
        second = re.findall(r'\d+<', tmp)
        report_content = report_content.replace(tmp, ">{}{}<".format("{}/ ".format(number_colored(add_comma(first[0][:-1]))), add_comma(second[0][:-1])))
    
    # for number % / number
    complex_number = re.findall(r'>\d+%/\d+<|>\d+.\d+%/\d+<|>\d+%/\d+.\d+<|>\d+%/\d+,\d+<|>\d+.\d+%/\d+.\d+<', raw_report_content)
    for tmp in complex_number:
        tmp_arr = tmp.split('/')
        first = tmp_arr[0].strip('>')
        second = add_comma_float(tmp_arr[1].strip('<')) if '.' in tmp_arr[1] or ',' in tmp_arr[1] else add_comma(tmp_arr[1].strip('<'))
        report_content = report_content.replace(tmp, ">{}{}<".format("{}/ ".format(number_colored(first)), second))
        
    # for number only
    simple_number = re.findall(r'>\d+<', raw_report_content)
    for tmp in simple_number:
        num = re.findall(r'\d+', tmp)
        report_content = report_content.replace(tmp, ">{}<".format(add_comma_float(num[0])))

    report_content = report_content.replace(".0<", "<")
        
    return report_content
