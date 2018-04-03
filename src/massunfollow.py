#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import os
import six
import sys
import common


J = os.path.join
C = os.path.abspath(os.getcwd())
uniquify = common.uniquify


def cliparse(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        argv.append('@'+J(C, 'unfollows.csv'))

    def callback(parser, **kw):
        parser.add_argument('--sync', default=True, action='store_false')
        parser.add_argument('ids', nargs='+')
    return common.cliparse(
        argv=argv,
        callback=callback,
        fromfile_prefix_chars='@',
        description='to unfollow twitter ids')


def do_unfollow(config, accounts, unfollows=None):
    if unfollows is None:
        unfollows = set()
    for i, data in six.iteritems(unfollows):
        for au, account in six.iteritems(data['accounts']):
            u = data['user']
            print('{0}: unfollowing {1} {2} {3}'.format(
                au, u.id, u.name, u.screen_name))
            try:
                account['api'].destroy_friendship(u.id)
            except (Exception,) as exc:
                msg = '{0}'.format(exc)
                if 'User not found' in msg:
                    print(' -> User not found')
                else:
                    raise


def main():
    parser, pargs = cliparse()
    wrapper = common.Wrapper.load(pargs.config)
    idunfollow = set()
    for i in pargs.ids:
        i = i.strip()
        if not i:
            continue
        try:
            idunfollow.add(int(i))
        except ValueError:
            idunfollow.add(wrapper.api.get_user(id=i).id)
    accounts = wrapper.accounts.values()
    followings = {}
    unfollows = {}
    if pargs.sync:
        for i in accounts:
            for uid, user in six.iteritems(wrapper.get_following(i)):
                f = followings.setdefault(uid, {})
                f.setdefault('user', user)
                fa = f.setdefault('accounts', {})
                fa[i['user']] = i
    for i in idunfollow:
        if i in followings:
            unfollows[i] = followings[i]
    do_unfollow(wrapper.config, accounts, unfollows)


if __name__ == '__main__':
    main()
# vim:set et sts=4 ts=4 tw=0:
