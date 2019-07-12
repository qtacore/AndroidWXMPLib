# -*- coding: utf-8 -*-
#
# Tencent is pleased to support the open source community by making QTA available.
# Copyright (C) 2016THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the BSD 3-Clause License (the "License"); you may not use this 
# file except in compliance with the License. You may obtain a copy of the License at
# 
# https://opensource.org/licenses/BSD-3-Clause
# 
# Unless required by applicable law or agreed to in writing, software distributed 
# under the License is distributed on an "AS IS" basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
#

'''将微信封装为一个浏览器
'''

import re

from wxapp import WxApp
from qt4w.browser import IBrowser
from qt4w.webcontrols import WebPage

from .util import WxBrowserPanel
from .main import MainPanel


class WeiXinBrowser(WxApp, IBrowser):
    '''微信浏览器
    '''
    def __init__(self, device, account, debug=False):
        '''打开微信并登录
        '''
        super(WeiXinBrowser, self).__init__(device, None if debug else True)
        if not debug: self.login(account)
        
    def open_url(self, url, page_cls=None):
        '''打开一个url，返回page_cls类的实例
        
        :param url: 要打开页面的url
        :type url:  string
        :param page_cls: 要返回的具体WebPage类,为None表示返回WebPage实例
        :type page_cls: Class
        '''
        main_panel = MainPanel(self)
        main_panel.open_url(url)
        if page_cls == None: page_cls = WebPage
        browser_panel = WxBrowserPanel(self)
        webview = browser_panel.Controls['webview']
        page = page_cls(webview)
        page.wait_for_ready()
        return page
    
    def find_by_url(self, url, page_cls=None, timeout=10):
        '''在当前打开的页面中查找指定url,返回WebPage实例，如果未找到，返回None
        
        :param url: 要查找的页面url
        :type url:  string
        :param page_cls: 要返回的具体WebPage类,为None表示返回WebPage实例
        :type page_cls: Class
        :param timeout: 查找超时时间，单位：秒
        :type timeout: int/float
        '''
        if page_cls == None: page_cls = WebPage
        browser_panel = WxBrowserPanel(self)
        webview = browser_panel.Controls['webview']
        page = page_cls(webview)
        page_url = page.url
        if page.url != url and not re.match(url, page_url): raise RuntimeError('当前页面[%s]不是：%s' % (page.url, url))
        return page
    
    def close(self):
        '''
        '''
        browser_panel = WxBrowserPanel(self)
        browser_panel.close()

    
