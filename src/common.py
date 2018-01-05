#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import lxml
import lxml.etree
import lxml.html
import yaml
import logging
import requests
import argparse
import os
import sys
import tweepy
from dogpile.cache import make_region

J = os.path.join
C = os.path.abspath(os.getcwd())

_cache = {
    'region': None,
}

_log = logging.getLogger('twitterblock')


def cacheapikey(prefix, cfg):
    return '{0}{1[apik]}{1[ak]}'.format(prefix, cfg)


def get_cache():
    if not _cache['region']:
        _cache['region'] = make_region().configure(
            'dogpile.cache.dbm',
            expiration_time=30*60,
            arguments={"filename": J(C, "cache.dbm")})
    return _cache['region']


def uniquify(seq):
    '''uniquify a list'''
    seen = set()
    return [x for x in seq
            if x not in seen and not seen.add(x)]


def consume_pages(callback, maxpages=1, *a, **kw):
    page = 1
    rets = []
    while True:
        ret = callback(page=page, *a, **kw)
        for i in ret:
            rets.append(i)
        page += 1  # next page
        if page > maxpages:
            break
    return rets


def consume(item):
    ret = []
    for i in tweepy.Cursor(item).items():
        ret.append(i)
    return ret


def cliparse(argv=None,
             callback=None,
             fromfile_prefix_chars=None,
             description='',
             **kw):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
            fromfile_prefix_chars=fromfile_prefix_chars,
            description=description)
    if callback:
        callback(parser, **kw)
    parser.add_argument('--config', default=J(C, 'config.yml'))
    pargs = parser.parse_args(argv)
    return parser, pargs


class Wrapper(object):

    def __init__(self):
        self.config = None
        self.accounts = {}
        self.api = None
        self.cache = None

    def load_config(self, configfile, partial=False):
        self.cache = get_cache()
        if configfile and os.path.exists(configfile):
            with open(configfile) as f:
                self.config = yaml.load(f.read())
            accounts, api = self.load_apis(partial=partial)
            for i in accounts:
                self.accounts[(i['apik'], i['ak'])] = i
            self.api = api
        else:
            raise ValueError('no config available, no api access')

    def me(self, api=None):
        if api is None:
            api = self.api
        a = api.auth
        return self.cache.get_or_create(
            'me{0.access_token}{0.consumer_key}'.format(a), lambda: api.me())

    def load_apis(self, partial=False):
        config = self.config
        accounts = config.setdefault('accounts', [])
        dapik = config.setdefault('apik', None)
        dapis = config.setdefault('apis', None)
        dak = config.setdefault('ak', None)
        das = config.setdefault('as', None)
        auth = tweepy.OAuthHandler(dapik, dapis)
        if not partial:
            auth.set_access_token(dak, das)
            for i in accounts:
                apik = i.setdefault('apik', dapik)
                apis = i.setdefault('apis', dapis)
                if not i['ak']:
                    raise ValueError('no access token')
                auth = tweepy.OAuthHandler(apik, apis)
                auth.set_access_token(i['ak'], i['as'])
                i['api'] = tweepy.API(auth)
                i['user'] = self.me(i['api']).screen_name
            api = tweepy.API(auth)
            config['user'] = self.me(api).screen_name
        else:
            accounts = []
            api = tweepy.API(auth)
        return accounts, api

    @classmethod
    def load(klass, configfile, partial=False):
        FORMAT = '%(asctime)s :: %(levelname)s :: %(message)s'
        logging.basicConfig(format=FORMAT)
        _log.setLevel(logging.DEBUG)
        self = klass()
        self.load_config(configfile, partial=partial)
        return self

    def get_notifs(self, account):
        _log.info('get notifs {0}'.format(account))

        def _do():
            with requests.Session() as s:
                notifs = 'https://twitter.com/i/notifications'
                cookies = {
                    'auth_token': account['wat']
                }
                req = s.get(notifs, cookies=cookies)
                tree = lxml.html.fromstring(req.text)
                usersids = tree.xpath("//div[@class='ActivityItem']//"
                                      "a[@data-user-id]"
                                      "/attribute::data-user-id")
                twids = tree.xpath("//div[@class='ActivityItem']//"
                                   "*[@data-item-type='tweet']"
                                   "/attribute::data-item-id")
                if not (twids or usersids):
                    print('Reauth WAT: {0}'.format(account))
                return twids, usersids
        return self.cache.get_or_create(
            cacheapikey('get_notifs{0}'.format(1), account), _do)

    def get_tweets_updates(self, account, pages=3):
        '''
        List all tweets and interacting user from
        the updates of an account (rt, favorite)
        '''
        _log.info('get tw up {0}'.format(account))
        rts = self.get_rt(account)
        tweets = {'rt': {}, 'l': {}, 't': {}}
        users = {}
        if account['wat']:
            twids, usersids = self.get_notifs(account)
            for tid in twids:
                t = self.get_tw(tid, api=account['api'])
                tweets['t'][t.id] = t
            for uid in usersids:
                try:
                    u = self.get_user_by_id(uid)
                except (Exception,) as exc:
                    print('{0}: {1}'.format(uid, exc))
                    u = None
                users[uid] = u
        for tweet in rts:
            rtos = self.get_rt_objs(account, tweet)
            for t in rtos:
                tweets['rt'][t.id] = t
                tweets['t'][t.id] = t
                users[tweet.user.id] = tweet.user
        return tweets, users

    def get_tw(self, tid, api=None):
        _log.info('get tw {0}'.format(tid))
        if api is None:
            api = self.api
        return self.cache.get_or_create(
            'get_tbyid{0}'.format(tid), lambda: api.get_status(id=tid))

    def get_timeline(self, uid, api=None, page=0):
        _log.info('get timeline {0} {1}'.format(uid, page))
        if api is None:
            api = self.api
        return self.cache.get_or_create(
            'get_eeeetimelinebyid{0}{1}'.format(uid, page),
            lambda: api.user_timeline(id=uid,
                                      count=99,
                                      page=page))

    def get_user_by_id(self, uid, api=None):
        _log.info('get user {0}'.format(uid))
        if api is None:
            api = self.api
        return self.cache.get_or_create(
            'get_ubyid{0}'.format(uid), lambda: api.get_user(id=uid))

    def get_rt_objs(self, account, tweet):
        tweet._api = account['api']

        def grt():
            return tweet.retweets()

        itm = self.cache.get_or_create(
            cacheapikey('rtobjs{0}'.format(tweet.id), account),
            grt,
            expiration_time=60*26)
        return itm

    def get_rt(self, account, count=50):
        _log.info('get rt {0}'.format(account))
        count += 1
        return self.cache.get_or_create(
            cacheapikey('rt{0}'.format(count), account),
            lambda: account['api'].retweets_of_me(count=count),
            expiration_time=60*15)

    def get_blocks(self, account):
        _log.info('get blocks {0}'.format(account))
        return self.cache.get_or_create(
            cacheapikey('blocks', account),
            lambda: consume(account['api'].blocks), expiration_time=60*30)

    def get_followers(self, account, maxpages=3):
        _log.info('get followers {0}'.format(account))
        return self.cache.get_or_create(
            cacheapikey('get_followers{0}'.format(maxpages), account),

            lambda: consume_pages(account['api'].followers, maxpages=maxpages))
# vim:set et sts=4 ts=4 tw=80:
