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
        argv = []
    def callback(parser, **kw):
        pass
        # parser.add_argument('--dry-run', default=False, action='store_true')
    return common.cliparse(
        argv=argv,
        callback=callback,
        fromfile_prefix_chars='@',
        description='export followings in sortable manner')


H = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<meta charset="UTF-8">
<style>
.container {
with: 100%;
}
.row {
    width: 300px;
    float: left;
    margin-right: 35px;
    margin-bottom: 25px;
    border: 1px solid black;
}
.row img {margin-left:10px;display: block;float: left;}
p.d a, p.d span   {display: block;margin-left: 75px; position: relative;}
.clear {clear:both;}
p.bio {margin: 0  10px 0 4px;}
</style>
<body><div  class=container>"""


def huser(fic, u):
    fic.write('<div class="row">')
    fic.write(
        (""
         "<p class='d'>"
         "  <img src='{2}' />"
         "  <a href='https://twitter.com/{0}' target='_blank'>@{0}</a>"
         "  <br/>"
         "  <span>{1}</span>"
         "</p>"
         "<p class='bio'>{3}<br/>{4}</p>"
         "").format(u.screen_name,
                    u.name,
                    u.profile_image_url,
                    u.description,
                    u.location))
    fic.write('</div>')


def main():
    parser, pargs = cliparse()
    wrapper = common.Wrapper.load(pargs.config)
    accounts = wrapper.accounts.values()
    followings = {}
    blocked = {}

    for i in accounts:
        for user in wrapper.get_blocks(i):
            blocked[user.screen_name] = user

    for i in accounts:
        for uid, user in six.iteritems(wrapper.get_following(i)):
            if user.screen_name in blocked:
                continue
            f = followings.setdefault(user.screen_name, {})
            f.setdefault('user', user)
            fa = f.setdefault('accounts', {})
            fa[i['user']] = i
    fids = [a for a in followings]
    fids.sort()

    followers = {}
    for i in accounts:
        for user in wrapper.get_followers(i):
            f = followers.setdefault(user.screen_name, {})
            if user.screen_name in blocked:
                continue
            f.setdefault('user', user)
            fa = f.setdefault('accounts', {})
            fa[i['user']] = i
    foids = [a for a in followers]
    foids.sort()
    with open('followers.html', 'w') as fic:
        fic.write(H)
        fic.write('<h2>Following</h2>')
        for s in fids:
            data = followings[s]
            u = data['user']
            huser(fic, u)
        fic.write('<div class="clear"/><br/>')
        fic.write('<h2>Followers (not in following)</h2>')
        for s in foids:
            if s in fids:
                continue
            data = followers[s]
            u = data['user']
            huser(fic, u)
        fic.write('</div></body></html>')


if __name__ == '__main__':
    main()
# vim:set et sts=4 ts=4 tw=0:
