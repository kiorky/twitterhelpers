#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import common


J = os.path.join
C = os.path.abspath(os.getcwd())
uniquify = common.uniquify


def cliparse(argv=None):
    def callback(parser, **kw):
        parser.add_argument('users', nargs='+')
    return common.cliparse(
        argv=argv,
        callback=callback,
        description='userids from usernames')


def main():
    parser, pargs = cliparse()
    wrapper = common.Wrapper.load(pargs.config)
    users = []
    for i in pargs.users:
        i = i.strip()
        if i[0] == '@':
            i = i[1:]
        users.append(i)
    for i in users:
        try:
            print(wrapper.api.get_user(id=i).id)
        except Exception:
            pass


if __name__ == '__main__':
    main()

# vim:set et sts=4 ts=4 tw=80:
