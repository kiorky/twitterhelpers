#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import common


J = os.path.join
C = os.path.abspath(os.getcwd())
uniquify = common.uniquify


def cliparse(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        argv.append('@'+J(C, 'list_ids.csv'))

    def callback(parser, **kw):
        parser.add_argument('--sync', default=True, action='store_false')
        parser.add_argument('ids', nargs='+')
    return common.cliparse(
        argv=argv,
        callback=callback,
        fromfile_prefix_chars='@',
        description='block twitter ids')


def do_block(config, accounts, idblocked=None, blocked=None):
    if idblocked is None:
        idblocked = set()
    if blocked is None:
        blocked = {}
    for i in accounts:
        to_block = i.setdefault('to_block', [])
        for ui in idblocked:
            if ui not in to_block:
                to_block.append(ui)
        to_block = uniquify([ui for ui in to_block if ui not in i['blocked']])
        i['to_block'] = to_block
        if to_block:
            for b in to_block:
                bname = blocked.get(b, None)
                if bname:
                    bname = bname.name
                else:
                    bname = str(b)
                print('{0}: blocking {1}'.format(i['user'], bname))
                try:
                    i['api'].create_block(id=b)
                except (Exception,) as exc:
                    msg = '{0}'.format(exc)
                    if 'User not found' in msg:
                        print(' -> User not found')
                    else:
                        raise


def main():
    parser, pargs = cliparse()
    wrapper = common.Wrapper.load(pargs.config)
    idblocked = set()
    blocked = {}
    for i in pargs.ids:
        if not i.strip():
            continue
        idblocked.add(int(i))
    accounts = wrapper.accounts.values()
    if pargs.sync:
        for i in accounts:
            i.setdefault('blocked', [])
            i.setdefault('blocked_users', [])
            for user in wrapper.get_blocks(i):
                idblocked.add(user.id)
                i['blocked'].append(user.id)
                i['blocked_users'].append(user)
                blocked[user.id] = user
    for i in idblocked:
        if i not in blocked:
            try:
                blocked[i] = wrapper.get_user_by_id(i)
            except (Exception,) as exc:
                print('{0}: {1}'.format(i, exc))
    do_block(wrapper.config, accounts, idblocked, blocked)


if __name__ == '__main__':
    main()
# vim:set et sts=4 ts=4 tw=80:
