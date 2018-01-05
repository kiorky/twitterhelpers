#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import tweepy
import common

from six.moves import input

J = os.path.join
C = os.path.abspath(os.getcwd())


def auth(consumer_key, consumer_secret, user=None, access_type='write'):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth_url = auth.get_authorization_url(access_type=access_type)
    print('Authorization URL: ' + auth_url)
    if user:
        print('use '+user)
    verifier = input('PIN: ').strip()
    auth.get_access_token(verifier)
    return (auth.access_token,
            auth.access_token_secret)


def cliparse(argv=None):
    def callback(parser, **kw):
        parser.add_argument('user', nargs='*')
    return common.cliparse(
        argv=argv,
        callback=callback,
        fromfile_prefix_chars='@',
        description='request oauth tokens')


def main():
    parser, pargs = cliparse()
    wrapper = common.Wrapper.load(pargs.config, partial=True)
    res = auth(wrapper.config['apik'],
               wrapper.config['apis'],
               user=pargs.user and pargs.user[0] or '')
    print("- ak: {0}\nas: {1}\n".format(*res))


if __name__ == '__main__':
    main()
# vim:set et sts=4 ts=4 tw=80:
