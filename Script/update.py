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
import json
import copy

TIME_FORMAT = '%Y-%m-%d %H:%M UTC+8'
FEED_URL = 'https://miaotony.xyz/atom.xml'


def get_rss():
    """
    Get RSS.
    :return: {FeedParserDict} feed: all feed info.
    """
    try:
        feed = feedparser.parse(FEED_URL)
        print("# Get RSS successfully!")
        return feed
    except Exception as e:
        print('# Get RSS ERROR!')
        print(e)


def parse_rss(fp):
    """
    Parse RSS & Generate a list of posts.
    :param fp: {FeedParserDict} all feed info.
    :return: {list} posts, a list of all posts.
    """
    posts = []
    for single_post in fp.entries:
        post = dict()
        try:
            post['title'] = single_post.get('title')
            post['link'] = single_post.get('link')
            post['summary'] = single_post.get('summary')  # 摘要

            # struct_time -> timestamp -> datetime
            publish_time = datetime.fromtimestamp(time.mktime(single_post.get('published_parsed')))
            publish_time += timedelta(hours=8)  # 转换为UTC+8
            tz = timezone('Asia/Shanghai')
            publish_time = publish_time.astimezone(tz)
            post['publishTime'] = publish_time.strftime(TIME_FORMAT)  # 发布时间

            update_time = datetime.fromtimestamp(time.mktime(single_post.get('updated_parsed')))
            update_time += timedelta(hours=8)  # 转换为UTC+8
            update_time = update_time.astimezone(tz)
            post['updateTime'] = update_time.strftime(TIME_FORMAT)  # 更新时间

            post['category'] = single_post.get('tags')
            print(post)
            if post:
                posts.append(post)
        except Exception as e:
            print("# Parse RSS ERROR!")
            print(e)

    posts.sort(key=lambda x: x['publishTime'], reverse=True)  # Sort posts according to their published time.
    print("# Parse RSS successfully! (Total: {} posts)".format(len(posts)))
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


def generate_markdown(posts_: list, generate_time):
    """
    Generate contents for Markdown file.
    :param posts_: {list} a list of all posts.
    :param generate_time: {datetime}
    :return: content {str}
    """
    env = Environment(loader=FileSystemLoader('./templates'))
    template = env.get_template('md_archives.j2')
    content = template.render(posts=posts_, generate_time=generate_time)
    print("# Generate Markdown successfully!")
    return content


def generate_json_and_save(posts_: list, generate_time):
    """
    Generate contents for JSON file. And save contents to `data.json` file.
    :param posts_: a list of all posts.
    :param generate_time: {datetime}
    # :return: content {str}
    """
    temp = dict()
    temp['data'] = posts_
    temp['generate_time'] = generate_time
    content = json.dumps(temp, ensure_ascii=False)
    print("# Generate JSON successfully!")

    # Save to json file
    with open('./data.json', 'w', encoding='utf-8') as f:
        f.write(content)


# def save_to_json_file(content: str):
#     """
#     Save contents to `data.json` file.
#     :param content: {str} raw string of output file.
#     """
#     with open('./data.json', 'w', encoding='utf-8') as f:
#         f.write(content)


def save_to_md_file(content_: str):
    """
    Save contents to `README.md` file.
    :param content_: {str} raw string of output file.
    """
    with open('../README.md', 'w', encoding='utf-8') as f:
        f.write(content_)


if __name__ == "__main__":
    fp = get_rss()
    if fp:
        posts = parse_rss(fp)

        now_time = datetime.utcnow() + timedelta(hours=8)
        now_time = now_time.strftime(TIME_FORMAT)

        content = generate_markdown(posts, now_time)
        generate_json_and_save(posts, now_time)
        save_to_md_file(content)
