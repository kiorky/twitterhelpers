#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import common
import re
import six


re_flags = re.M | re.U | re.S | re.I
J = os.path.join
C = os.path.abspath(os.getcwd())
uniquify = common.uniquify


def cliparse(argv=None):
    def callback(parser, **kw):
        parser.add_argument('--no-followers',
                            default=False, action='store_true')
        parser.add_argument('--no-notifs',
                            default=False, action='store_true')
        parser.add_argument('--pages', default=1, type=int)
    return common.cliparse(
        argv=argv,
        callback=callback,
        description='userids from usernames')


def is_ham(item, cfg):
    if item['screen_name'].lower() in cfg.get('ham', []):
        return True
    return False


def spammers(l, cfg):
    ham, spam = [], []
    is_spam = re.compile(
        '('
        '(do you like fast)'
        '|(Do you like it gently)'
        '|(Dancing / Your favorite)'
        '|(Come to my site)'
        '|(Come to me)'
        '|(Come in!)'
        '|(I want you...)'
        '|(How do you like me?)'
        '|(model / fitness)'
        '|(my private videos)'
        '|(model.*actress.*https?://t\.co)'
        '|((lofavorite|ver|unicorn|beauty|model| fan|fitness|travel|traveler).?'  # noqa
        ' (waiting you at|check this|click at|waiting you at|come on|come to me|check out|go to) https?://)'  # noqa
        '|(you want me)'
        '|(voice actress)'
        '|(I want you dear...|Do you like me)'
        '|(cosplay)'
        '|(for.*18.*y)'
        '|(💥|😚|💚|😙|💗|💖|🍒|💝)'  # noq
        ')'
    )
    for item in l:
        d = item['description']
        if (
            (is_spam.search(d) or is_spam.search(d.lower())) and
            not is_ham(item, cfg)
        ):
            spam.append(item)
        else:
            ham.append(item)
    return ('ham', ham), ('spam', spam)


def append_ret(usersd, user):
    ret = {}
    for n in ['description', 'id', 'name', 'screen_name']:
        ret[n] = getattr(user, n)
    if ret not in usersd:
        usersd.append(ret)
    return usersd


def main():
    parser, pargs = cliparse()
    wrapper = common.Wrapper.load(pargs.config)
    accounts = wrapper.accounts.values()
    usersd = []
    if not pargs.no_followers:
        for i in accounts:
            for user in wrapper.get_followers(i):
                append_ret(usersd, user)
    blocked = {}
    if not pargs.no_notifs:
        for i in accounts:
            tw, users = wrapper.get_tweets_updates(i)
            for uid, u in six.iteritems(users):
                append_ret(usersd, u)
            for u in wrapper.get_blocks(i):
                blocked[u.id] = u
    import pdb;pdb.set_trace()  ## Breakpoint ##
    for cat, l in spammers(usersd, wrapper.config):
        for i in l:
            if i['id'] in blocked:
                continue
            print('{cat} {i[id]: <20}  '
                  '{i[screen_name]: <35} '
                  '{i[name]: <35} '
                  '{i[description]}'.format(**locals()).replace('\n', ' '))


if __name__ == '__main__':
    main()
# vim:set et sts=4 ts=4 tw=0:
