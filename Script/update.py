#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
update.py
Crawl data from RSS, then generate Markdown file.
获取 RSS 数据，根据模板生成 Markdown 文档。
https://github.com/miaotony/BlogArchives

@Author: MiaoTony
@Time: 20200319
"""

import feedparser
import time
from datetime import timedelta, datetime
from pytz import timezone
from jinja2 import Environment, FileSystemLoader

TIME_FORMAT = '%Y-%m-%d %H:%M UTC+8'
FEED_URL = 'https://miaotony.xyz/atom.xml'


def parse_rss():
    """
    Parse RSS & Generate a post list.
    :return: {list} posts, a list of all posts.
    """
    fp = feedparser.parse(FEED_URL)
    posts = []
    for single_post in fp.entries:
        post = dict()
        post['title'] = single_post.get('title')
        post['link'] = single_post.get('link')
        post['summary'] = single_post.get('summary')  # 摘要

        # struct_time -> timestamp -> datetime
        publish_time = datetime.fromtimestamp(time.mktime(single_post.published_parsed))
        publish_time += timedelta(hours=8)  # 转换为UTC+8
        tz = timezone('Asia/Shanghai')
        publish_time = publish_time.astimezone(tz)
        post['publishTime'] = publish_time.strftime(TIME_FORMAT)  # 发布时间

        post['category'] = single_post.get('tags')
        # print(post)
        posts.append(post)
    posts.sort(key=lambda x: x['publishTime'], reverse=True)  # Sort according to publish time
    return posts


# An Example
# {'title': 'CTF | XCTF高校战“疫”网络安全分享赛 WriteUp', 'title_detail': {'type': 'text/plain', 'language': None,
# 'base': 'https://miaotony.xyz/atom.xml', 'value': 'CTF | XCTF高校战“疫”网络安全分享赛 WriteUp'}, 'links':
# [{'href': 'https://miaotony.xyz/2020/03/15/CTF_2020XCTF_gxzy/', 'rel': 'alternate', 'type': 'text/html'}],
# 'link': 'https://miaotony.xyz/2020/03/15/CTF_2020XCTF_gxzy/',
# 'id': 'https://miaotony.xyz/2020/03/15/CTF_2020XCTF_gxzy/',
# 'guidislink': False, 'published': '2020-03-15T12:00:00.000Z', 'published_parsed': time.struct_time(tm_year=2020,
# tm_mon=3, tm_mday=15, tm_hour=12, tm_min=0, tm_sec=0, tm_wday=6, tm_yday=75, tm_isdst=0), 'updated':
# '2020-03-17T16:38:48.613Z', 'updated_parsed': time.struct_time(tm_year=2020, tm_mon=3, tm_mday=17, tm_hour=16,
# tm_min=38, tm_sec=48, tm_wday=1, tm_yday=77, tm_isdst=0),
# 'summary': '前不久水了一下XCTF的高校战“疫”网络安全分享赛，然而菜死了都没做出几道题，随便写点点WriteUp和感受吧。',
# 'summary_detail': {'type': 'text/html', 'language': None, 'base': 'https://miaotony.xyz/atom.xml',
# 'value': '前不久水了一下XCTF的高校战“疫”网络安全分享赛，然而菜死了都没做出几道题，随便写点点WriteUp和感受吧。'},
# 'tags': [{'term': 'CTF', 'scheme': 'https://miaotony.xyz/categories/CTF/', 'label': None}],
# 'tag': {'term': 'WriteUp', 'scheme': 'https://miaotony.xyz/tags/WriteUp/'}}


def generate_markdown(posts: list):
    """
    Generate contents for Markdown file.
    :param posts: a list of all posts.
    :return: content {str}
    """
    now_time = datetime.utcnow() + timedelta(hours=8)
    now_time = now_time.strftime(TIME_FORMAT)

    env = Environment(loader=FileSystemLoader('./templates'))
    template = env.get_template('md_archives.j2')
    contents = template.render(posts=posts, updateTime=now_time)
    return contents


def save_to_file(content: str):
    """
    Save contents to `README.md` file.
    :param content: {str} raw string of output file.
    """
    with open('../README.md', 'w', encoding='utf-8') as f:
        f.write(content)


if __name__ == "__main__":
    posts = parse_rss()
    content = generate_markdown(posts)
    save_to_file(content)
