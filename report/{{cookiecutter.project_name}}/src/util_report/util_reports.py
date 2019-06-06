# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import pyspark.sql.functions as F
import yaml
from datetime import datetime, timedelta


def get_block_data_from_pyspark_df(table_headers, table_arrays, table_data, grand_total_label=False):
    tuples = list(zip(*table_headers))
    
    index = pd.MultiIndex.from_tuples(tuples, names=['', 'Doanh thu (triệu VND)'])
    df = pd.DataFrame(table_data, 
                      index=table_arrays, 
                      columns=index)
    
    if grand_total_label:
        total = df.apply(np.sum)
        df = df.append(pd.DataFrame(total.values, index=total.keys()).T, ignore_index=True)
    
    return df


def get_table_css():
    css = """
    .dataframe {
        font-size: 9.0pt; font-family: Roboto Mono;
        border-collapse: collapse; border-style: DOTTED; border-width: 1px; border-color: blue;
    }
    .dataframe td, th{
        font-size: 10pt; padding: 5px;
    }
    .dataframe thead > tr{
        background-color: rgb(41,54,119);color: rgb(255,255,255)
    }
    .dataframe tbody > tr:nth-child(1){
        background-color: blue;color: rgb(255,255,255);font-weight:bold;
    }
    """
    
    return css

def genere_table_html(pd_dataframe):
    """
    Function get table html for pandas dataframe
    """
    table_html = pd_dataframe.to_html()
    
    return table_html


def generate_full_html(pd_table_list):
    pd.set_option('colheader_justify', 'center')
    
    full_html = '''
    <html>
      <head>
          <meta charset="UTF-8">
          <style>{css}</style>
      </head>
      <body>
    '''.format(css=get_table_css())
    
    for pd_table in pd_table_list:
        full_html += genere_table_html(pd_table)
    
    full_html += '''
        </body>
    </html>
    '''
    
    return full_html


def make_pivot_table(pd_df, index_cols, columns, value_col, default_fillna='', agg_func="sum", margins=True):
    # make pivo
    pivot_df = pd_df.pivot_table(
        index=index_cols, 
        columns=columns, 
        values=value_col, 
        aggfunc=agg_func, 
        margins=margins
    )
    
    return pivot_df.fillna(default_fillna) if default_fillna != '' else pivot_df


def make_single_table_report(pivot_pd, table_headers, grand_total_label=False):
    # mutilple index defination
    table_arrays = list(pivot_pd.index)
    
    # get pandas mutilple index 
    block_data = get_block_data_from_pyspark_df(table_headers, table_arrays, pivot_pd.values, grand_total_label)
    
    return genere_table_html(block_data)


def get_channel_label(channel_int):
    channel_mapping = {1: 'Showroom', 2: 'Chat', 3: 'Phone', 4: 'Apps'}
    try:
        return channel_mapping[channel_int]
    except:
        return 'Unknown'
    

def round_df(pd_df, decimals=2):
    for pd_df_col in pd_df.columns:
        pd_df[pd_df_col] = pd_df[pd_df_col].apply(lambda x:round(x,decimals))
        
    return pd_df


def get_list_sort_province():
    return [
        'Hà Nội', 'Nghệ An', 'Vĩnh Phúc', 'Bắc Giang', 'Thái Nguyên', 'Bắc Ninh', 'Thanh Hóa', 'Quảng Ninh', 'Hải Phòng', 'Các tỉnh khác miền Bắc',
        'Đà Nẵng', 'Quảng Ngãi', 'Quảng Trị', 'Lâm Đồng', 'Đắk Lắk', 'Ninh Thuận', 'Khánh Hòa', 'Các tỉnh khác miền Trung',
        'Hồ Chí Minh', 'Đồng Nai', 'Bình Dương', 'Bà Rịa - Vũng Tàu', 'Sóc Trăng', 'Bến Tre', 'Đồng Tháp', 'Cần Thơ', 'Kiên Giang', 'Long An',
        'Tây Ninh', 'Tiền Giang', 'Cà Mau', 'Các tỉnh khác miền Nam'
    ]


def get_list_sort_channel(channels):
    sorted_channels = []
    for channel in channels:
        if channel in ['Doanh thu thuần (tỷ VND)', 'Tỷ suất lợi nhuận gộp (%)']:
            sorted_channels.insert(0, channel)
        elif channel == 'Store':
            sorted_channels.insert(1, channel)
        elif channel == 'Online':
            sorted_channels.insert(2, channel)
        else:
            sorted_channels.append(channel)
            
    return sorted_channels


def make_custom_sort_by_cat(pd_df):
    list_cat_sorted = []
    for cat_id in pd_df.index:
        sep1 = '/'
        cat_id = cat_id.split(sep1, 1)[0]
        sep2 = '.'
        cat_id = cat_id.split(sep2, 1)[0]
        if cat_id in ['Toàn công ty', 'All']:
            cat_id = '0000' + cat_id
        elif cat_id.startswith('NGH'):
            cat_id = cat_id[-2:] + '-00' + cat_id
        elif cat_id.startswith('KHAC'):
            cat_id = cat_id[-2:] + '-W' + cat_id
        list_cat_sorted.append(cat_id)
    pd_df["sorted_col"] = list_cat_sorted
    
    return pd_df.sort_values(by='sorted_col').drop(columns=['sorted_col'])


def make_custom_sort_by_list(pd_df, col_to_sort, sort_values, keep_sort_col=False):
    list_sorted = []
    for el in pd_df['{}'.format(col_to_sort)]:
        el_order = sort_values.index(el)
        list_sorted.append(el_order)
        
    pd_df["sorted_col"] = list_sorted
    
    if keep_sort_col:
        return pd_df.sort_values(by='sorted_col')
    else:
        return pd_df.sort_values(by='sorted_col').drop(columns=['sorted_col'])


def make_custom_sort_by_list_and_index(pd_df, sort_values, keep_sort_col=False):
    list_sorted = []
    for el in pd_df.index:
        el_order = sort_values.index(el)
        list_sorted.append(el_order)
        
    pd_df["sorted_col"] = list_sorted
    
    if keep_sort_col:
        return pd_df.sort_values(by='sorted_col')
    else:
        return pd_df.sort_values(by='sorted_col').drop(columns=['sorted_col'])


def divide_cols(pd_df, cols, divide_unit=1000000):
    for col in cols:
        pd_df[col] = pd_df[col].apply(lambda x: float(x)/float(divide_unit))

        
def round_cols(pd_df, cols, decimals=2):
    for col in cols:
        pd_df[col] = pd_df[col].apply(lambda x: round(x, decimals))
        
        
def get_sum_row(pd_df, row_label=False):
    """ Get sum row for pandas dataframe """
    sum_row = pd_df.sum(axis=0)
    pd_sum=pd.DataFrame(data=sum_row).T
    
    if row_label:
        # change sum row index
        pd_sum.index = [row_label]
    
    return pd_sum


def add_sum_row(pd_df, position="first", row_label=False):
    """ Return new pandas dataframe with sum row """
    pd_sum = get_sum_row(pd_df, row_label)
    if position == "first":
        return pd.concat([pd_sum, pd_df], sort=False)
    else:
        return pd.concat([pd_df, pd_sum], sort=False)
    

def get_header(header_info, report_date):
    header_list = []
    for level_item in header_info:
        if 'dd/mm_report_date' in level_item['val']:
            level_item['val'] = level_item['val'].replace('dd/mm_report_date', report_date.strftime('%d-%m'))
        if 'dd/mm_pre_report_date' in level_item['val']:
            level_item['val'] = level_item['val'].replace('dd/mm_pre_report_date', (report_date-timedelta(days=7)).strftime('%d-%m'))
        if ' mm' in level_item['val']:
            level_item['val'] = level_item['val'].replace('mm', str(report_date.date().month))
        header_list.append(level_item)
    
    return [header_list]


def get_data_before_render(config_table, pd_df, table_class=''):
    headers = []
    for k, v in config_table['headers'].items():
        headers.extend(get_header(v, report_date))
        
    return {
        'header_list': headers,
        'row_details': pd_to_custom_object(pd_df, config_table['highlight_index']),
        'footer_list': [],
        'table_class': table_class
    }


def get_styles(file_style_name):
    styles = yaml.safe_load(open('util_report/styles/{}'.format(file_style_name)))
    style = "<style>"
    for k, v in styles.items():
        key_styles = [];
        for kk, vv in v.items():
            key_styles.append(kk + ':' + vv)
        style += k + "{" + ";".join(key_styles) + ";}"
    style += "</style>"
    
    return style 


def pd_to_custom_object(pd_df, highlight_index={}):
    row_details = []
    tr = []
    for pd_index, pd_row in pd_df.iterrows():
        td = []
        row_number_class = 'row_number'
        if pd_index in highlight_index.keys():
            row_number_class = 'sub_header_number'
            td.append({
                'val': pd_index, 
                'class': highlight_index[pd_index]['class'] if 'class' in highlight_index[pd_index] else 'sub_header_text', 
                'colspan': highlight_index[pd_index]['colspan'] if 'colspan' in highlight_index[pd_index] else 1})
        else:
            td.append({'val': pd_index, 'class': 'row_number_left'})
        for i in pd_row.index:
            td.append({
                'val': pd_row[i],
                'class': row_number_class
            })
        tr.append(td)
        
    row_details.extend(tr)
    
    return row_details


def change_values(pd_df, indexs, cols, val=''):
    for index in indexs:
        for col in cols:
            pd_df.loc['{}'.format(index)]['{}'.format(col)] = val
            
    return pd_df

def custom_divide(pd_df, divisor_col, dividend_col, zero_val=0):
    res = []
    for i in pd_df.index:
        if pd_df.loc[i][dividend_col] == 0:
            res.append(zero_val)
        else:
            res.append(float(pd_df.loc[i][divisor_col])/float(pd_df.loc[i][dividend_col]))
            
    return res


@F.udf
def title_string(str_input):
    if str_input:
        return str_input.title()
    else:
        return str_input
    
@F.udf
def str_to_number(str_input):
    return str_input.replace(',', '').replace('.', '')