#coding: utf-8 
from __future__ import print_function, unicode_literals

from email.utils import parseaddr


# import sys
# if sys.version[0] == '2':
#     from importlib import reload
#     reload(sys)
#     sys.setdefaultencoding("utf-8")

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email import charset
from email.generator import Generator
import smtplib
import os
import re
from jinja2 import Environment, FileSystemLoader

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
MAIL_TEMPLATE_FOLDER = 'mail_templates'

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

def send_mail_with_cc(to, cc, subject, content):
    from_address = "Phong Vu Report System <reportsystem@teko.vn>"
    print('send_mail_with_cc: from %s to %s' % (from_address, to[0]))
    #bcc = "bccperson1@gmail.com,bccperson2@yahoo.com"

    rcpt = cc + to
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = ','.join(to)
    msg['Cc'] = ','.join(cc)
    #msg['Bcc'] = bcc

    # Record the MIME types of both parts - text/plain and text/html.
    part = MIMEText(content, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("reporting@phongvu.vn", "ugqywgmsripezhpt")
    s.sendmail(from_address, rcpt, msg.as_string())
    s.quit()
