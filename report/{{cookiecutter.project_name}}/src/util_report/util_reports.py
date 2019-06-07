# -*- coding: utf-8 -*-

import pandas as pd

def get_channel_label(channel_int):
    channel_mapping = {1: 'Showroom', 2: 'Chat', 3: 'Phone', 4: 'Apps'}
    try:
        return channel_mapping[channel_int]
    except:
        return 'Unknown'


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