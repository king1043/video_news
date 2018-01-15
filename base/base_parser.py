import sys
sys.path.append('..')
import init
import base.constance as Constance
import utils.tools as tools
from utils.log import log
from db.mongodb import MongoDB
from db.elastic_search import ES

db = MongoDB()
es = ES()


def remove_table(tab_list):
    for tab in tab_list:
        db.delete(tab)


def reset_table(tab_list):
    for tab in tab_list:
        db.update(tab, {'status': 3}, {'status': 0})


def add_url(table, site_id='', url='', depth=0, remark='', status=Constance.TODO, title='', origin='', domain='',
            retrieval_layer=0, image_url='', release_time=''):
    url_dict = {'site_id': site_id, 'url': url, 'depth': depth, 'remark': remark, 'status': status, 'title': title,
                'origin': origin, 'release_time': release_time, 'domain': domain,
                'record_time': tools.get_current_date(), 'image_url': image_url, 'retrieval_layer': retrieval_layer}
    return db.add(table, url_dict)


def update_value(table, attrs_old={}, attrs_new={}):
    db.update(table, attrs_old, attrs_new)


def update_url(table, url, status):
    db.update(table, {'url': url}, {'status': status})


def add_website_info(table, site_id, url, name, domain='', ip='', address='', video_license='', public_safety='',
                     icp='', contain_outlink=False):
    '''
    @summary: 添加网站信息
    ---------
    @param table: 表名
    @param site_id: 网站id
    @param url: 网址
    @param name: 网站名
    @param domain: 域名
    @param ip: 服务器ip
    @param address: 服务器地址
    @param video_license: 网络视听许可证|
    @param public_safety: 公安备案号
    @param icp: ICP号
    ---------
    @result:
    '''

    # 用程序获取domain,ip,address,video_license,public_safety,icp 等信息
    domain = tools.get_domain(url)

    site_info = {
        'contain_outlink': contain_outlink,
        'site_id': site_id,
        'name': name,
        'domain': domain,
        'url': url,
        'ip': ip,
        'address': address,
        'video_license': video_license,
        'public_safety': public_safety,
        'icp': icp,
        'read_status': 0,
        'record_time': tools.get_current_date()
    }
    db.add(table, site_info)




def find_ipcategory(ip_num):
    try:
        info = db.find('ip_mappings', {'end': {'$gte': ip_num}, 'start': {'$lte': ip_num}})
    except:
        return
    return list(info)[0]['address']


def is_have_video_by_site(domain):
    '''@summary: 根据特定网站的特征来判断'''
    feas = db.find('FeaVideo_site', {'domain': domain})

    if feas:
        return True
    else:
        return False


def is_have_video_by_judge(title, content):
    '''
    @summary: 根据title 和 content 来判断 （正负极）
    ---------
    @param title:
    @param content:
    ---------
    @result:
    '''

    text = title + content

    feas = db.find('FeaVideo_judge')

    for fea in feas:
        not_video_fea = fea['not_video_fea'].split(',')
        video_fea = fea['video_fea'].split(',')

        if tools.get_info(text, not_video_fea):
            return False

        if tools.get_info(text, video_fea):
            return True

    return False


def is_have_video_by_common(html):
    '''
    @summary: 根据html源码来判断
    ---------
    @param html: html源码
    ---------
    @result:
    '''

    feas = db.find('FeaVideo_common')

    for fea in feas:
        video_fea = fea['video_fea'].split(',')

        if tools.get_info(html, video_fea):
            return True

    return False

def save_video_info(release_time='', content='', url='', author='', title='', image_url='', site_name='', play_count = None, comment_count = None, praise_count = None, summary = '', time_length = None):
    domain = tools.get_domain(url)
    uuid = tools.get_uuid(title, domain)

    if es.get('video_news', uuid):
        log.debug(title + ' 已存在')
        return False

    content_info = {
        'domain':domain,
        'uuid' : uuid,
        'site_name': site_name,
        'image_url': image_url,
        'title': title,
        'author': author,
        'url': url,
        'content': content,
        'release_time': tools.format_date(release_time),
        'play_count':play_count,
        'comment_count':comment_count,
        'praise_count':praise_count,
        'time_length':time_length,
        'record_time':tools.get_current_date(),
        'summary':summary
    }
    log.debug(tools.dumps_json(content_info))

    es.add('video_news', content_info, content_info['uuid'])
    return True



