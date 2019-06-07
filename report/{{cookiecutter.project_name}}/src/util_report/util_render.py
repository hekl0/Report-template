#coding: utf-8 
import os
import re
import yaml
from tkmail.tkmail import *
from jinja2 import Environment, FileSystemLoader

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
MAIL_TEMPLATE_FOLDER = 'mail_templates'

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


def get_data_before_render(config_table, pd_df, report_date, table_class=''):
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


def render_header(config_header):
    header = render_content('header.html', {
        'style': get_styles('eod.yml'), 
        'data': {
            'title': config_header['report_name'],
            'extras_information': config_header['extras_information']
        }
    })
    return header


def render_table(df):
    return render_content('table.html', {'data': df})


def render_content(template_file=None, raw_content=None):
    """
    Render content from mail template
    template_file is the name of file template which you want and raw_content is a dictionary
    :param template_file:
    :param raw_content:
    :return:
    """
    if not template_file:
        return False

    # load template file content to render
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                         trim_blocks=True)
    # get template and then render content of raw_content
    if raw_content:
        build_content = j2_env.get_template('%s/%s' % (MAIL_TEMPLATE_FOLDER, template_file)).render(raw_content)
    else:
        return False
    
    response = re.sub('\n +', '', build_content)
    response = re.sub('\n+', '', response)
    response = re.sub('> +', '>', response)
    return response


def write_to_file_html(file, html):
    from yattag import indent
    html_pretty = indent(
        html,
        indentation = '    ',
        newline = '\r\n',
        indent_text = True
    )
    #Write to file 
    f = open(file, "wb")
    f.write(str(html_pretty).encode('utf-8'))
    f.close()
    print("write to file done")


def send_mail_with_cc(email_config, report_date, content):
    email_obj = Email('smtp.gmail.com', 587, email_config['smtp']['username'], email_config['smtp']['password']) 
    email_obj.send_mail(
        '{} <{}>'.format(email_config['from'], email_config['smtp']['username']), 
        email_config['to'], 
        email_config['subject'].replace('dd/mm/yyyy', report_date.strftime('%d-%m-%Y')), 
        content, 
        email_config['cc']
    )
    print("send email done")