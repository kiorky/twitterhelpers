#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import common
import re
import six
from IPython import embed


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


def is_ham(item):
    if item['screen_name'].lower() in [
        'kiorky', 'valk', 'res1854006', 'res1854006b',
        'res122188800', 'valkphotos',
    ]:
        return True
    return False

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
    i = [a for a in accounts if a['user'] == wrapper.config['main']][0]
    api = i['api']
    tws = wrapper.get_timeline(uid=wrapper.config['main'], api=i['api'], page=1)
    embed()           
    #for t in tws[1:20]:api.destroy_status(t.id); 



if __name__ == '__main__':
    main()
# vim:set et sts=4 ts=4 tw=0:
