# -*- coding: UTF-8 -*-
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
'''公共库
'''

import os
import time
from qt4a.andrcontrols import Window, TextView, WebView, ImageView, Button, EditText, ListView, ChromiumWebView
from qt4a.qpath import QPath
from qt4a.androiddriver.util import logger
from tuia.exceptions import ControlNotFoundError


class MultiWindow(Window):
    Activity = ''
    Activity2 = ''

    def __init__(self, app):
        super(MultiWindow, self).__init__(app, False)

    def post_init(self):
        '''真正等待Activity的逻辑
        '''
        timeout = 20
        time0 = time.time()
        current_activity = None
        while time.time() - time0 < timeout:
            current_activity = self.device.current_activity
            if current_activity == self.__class__.Activity or current_activity == self.__class__.Activity2:
                if current_activity != self.__class__.Activity:
                    # 修正为当前Activity
                    for key in self._locators.keys():
                        self._locators[key]['activity'] = current_activity
                break
            time.sleep(0.5)
        else:
            raise ControlNotFoundError('Current window: %s not in (%s, %s)' % (current_activity, self.__class__.Activity, self.__class__.Activity2))   


class X5WebView(WebView):
    '''QQ浏览器X5内核
    '''
    is_chromium = True


class XWalkChromiumWebView(ChromiumWebView):
    '''XWalk  WebView实现
    '''

    def __init__(self, *args, **kwargs):
        super(XWalkChromiumWebView, self).__init__(*args, **kwargs)

    def create_socket(self):
        '''创建socket对象
        '''
        self._service_name = 'xweb_devtools_remote_%d' % self._pid
        try:
            sock = self._device.adb.create_tunnel(
                self._service_name, 'localabstract')
            if sock:
                return sock
        except:
            logger.warn('create socket tunnel %s failed' % self._service_name)
        self._driver.call_static_method(
            'org.xwalk.core.internal.XWalkPreferencesInternal', 'setValue', self.hashcode, '', 'remote-debugging', True)
        return self.create_socket()


class XWalkWebView(WebView):
    '''XWalk内核
    '''
    is_chromium = True

    @property
    def webview_impl(self):
        '''
        '''
        if self._webview_impl == None:
            self._webview_impl = XWalkChromiumWebView(title=self.__class__.title, url=self.__class__.url, *self._args, **self._kwargs)
        return self._webview_impl


def MiniProgramWebView(webview_cls):
    '''动态创建小程序WebView类
    '''
    attrs = {
        'title': r'^wx.+:VISIBLE$'
    }
    return type('MiniProgramWebView_%s' % webview_cls.__name__, (webview_cls,), attrs)


class WXBrowserPanel(Window):
    '''内置浏览器，不要随便修改这个类的Activity，可以在继承的类里重写Acticity
    '''
    Process = 'com.tencent.mm:tools'
    Activity = 'com.tencent.mm.plugin.webview.ui.tools.WebViewUI'  # web进程内置浏览器窗口

    def __init__(self, wxapp):
        super(WXBrowserPanel, self).__init__(wxapp)
        self.update_locator({
            '系统WebView1': {'type': WebView, 'root': self, 'locator': QPath('/Desc="网页视图" && Visible="True"&& Instance="0"')},
            '系统WebView2': {'type': WebView, 'root': self, 'locator': QPath('/Type="WebView$b" && Visible="True"&& Instance="0"')},
            # 存在多个时只关心第一个
            'X5WebView': {'type': X5WebView, 'root': self, 'locator': QPath('/Type="TencentWebViewProxy$InnerWebView" && Visible="True" && Instance=0')},
            'XWalkWebView': {'type': XWalkWebView, 'root': self, 'locator': QPath(r'/Type~="XWalkContent\$\d+" && Visible="True"&& Instance="0" ')},
            # 'webview': {'type': WebView, 'root': self, 'locator': QPath('')},
            '标题': {'type': TextView, 'root': self, 'locator': QPath('/Id="text1"')},
            # 待测试
            '返回': {'type': ImageView, 'root': self, 'locator': QPath('/Desc="返回"')},
        })
        self._wait_for_window = False  # 是否等待窗口标题变化
        if self.device.get_current_activity() == self.Activity:
            self._wait_for_window = True  # 待测试

    def __getitem__(self, index):
        '''主要用于解决WebView会变问题
        '''
        if index == 'webview':
            timeout = 60
            time0 = time.time()
            while time.time() - time0 < timeout:
                if self.Controls["系统WebView1"].exist():
                    return self.Controls["系统WebView1"]
                elif self.Controls["系统WebView2"].exist():
                    return self.Controls["系统WebView2"]
                elif self.Controls["X5WebView"].exist():
                    return self.Controls["X5WebView"]
                elif self.Controls["XWalkWebView"].exist():
                    return self.Controls["XWalkWebView"]
                time.sleep(0.5)
            else:
                raise ControlNotFoundError(index)
        else:
            return super(WXBrowserPanel, self).__getitem__(index)

    def post_init(self):
        '''窗口自定义初始化逻辑
        '''
        if not self._wait_for_window:
            return
        if not self.Controls['标题'].exist():
            return
        timeout = 4
        title = self.Controls['标题'].text
        time0 = time.time()
        while time.time() - time0 < timeout:
            self.Controls['标题']._hashcode = 0  # 重新获取顶层窗口控件
            new_title = self.Controls['标题'].text
            if new_title and new_title != title:
                return

            time.sleep(0.5)

    def close(self):
        self.Controls["返回"].click()


class WebAuthorizeDialog(Window):
    '''WebView授权窗口
    '''
    Process = 'com.tencent.mm:tools'
    Activity = 'com.tencent.mm.plugin.webview.ui.tools.WebViewUI'

    def __init__(self, app):
        super(WebAuthorizeDialog, self).__init__(app)
        self.update_locator({'微信登录': {'type': TextView, 'root': self, 'locator': QPath('/Text="微信登录"')},
                             '允许': {'type': Button, 'root': self, 'locator': QPath('/Text="允许"')},
                             })

    def exist(self, timeout=5):
        '''该窗口是否存在
        '''
        time0 = time.time()
        while time.time() - time0 < timeout:
            if self.Controls['微信登录'].exist():
                return True
            time.sleep(0.5)
        return False

    def agree(self):
        '''允许
        '''
        self.Controls['允许'].click()


class ActionBarEditText(EditText):
    '''com.tencent.mm.ui.tools.ActionBarSearchView$ActionBarEditText
    '''
    pass


class TBSDownloadDialog(Window):
    '''TBS升级窗口
    '''

    Activity = 'com.tencent.mm.plugin.appbrand.ui.AppBrandTBSDownloadProxyUI'
    Process = 'com.tencent.mm:sandbox'

    def __init__(self, app):
        super(TBSDownloadDialog, self).__init__(app)
        self.update_locator({'取消': {'type': Button, 'root': self, 'locator': QPath('/Text="取消"')},
                             '升级': {'type': Button, 'root': self, 'locator': QPath('/Text="升级"')},
                             })

    def exist(self):
        '''窗口是否存在
        '''
        timeout = 15
        time0 = time.time()
        while time.time() - time0 < timeout:
            if self.Controls["升级"].exist():
                return True
            time.sleep(0.5)
        return False

    def upgrade(self):
        self.Controls["升级"].click()

    def close(self):
        self.Controls["取消"].click()


class NoScrollListView(ListView):
    '''不需要滚动的ListView
    '''

    def update(self):
        self._children = self.children
        self._item_count = len(self._children)
        self._last_visible_position = self._item_count - 1

    def scroll_up_one_page(self):
        pass

    def scroll_down_one_page(self):
        pass


class WXUpdateDialog(Window):
    '''微信升级弹窗
    '''
    Activity = 'com.tencent.mm.sandbox.updater.AppInstallerUI'
    Process = 'com.tencent.mm:sandbox'

    def __init__(self, app):
        super(WXUpdateDialog, self).__init__(app)
        self.update_locator({
            '标题': {'type': TextView, 'root': self, 'locator': QPath('/Text="更新"')},
            '取消': {'type': Button, 'root': self, 'locator': QPath(r'/Text~="\s*取消\s*"')},
            '立即安装': {'type': Button, 'root': self, 'locator': QPath('/Text="立即安装"')},
        })

    def close(self):
        self.Controls['取消'].click()
        dialog = WXCancelUpdateConfirmDialog(self)
        dialog.close()


class WXCancelUpdateConfirmDialog(Window):
    '''取消升级确认弹窗
    '''
    Activity = 'com.tencent.mm.sandbox.updater.AppInstallerUI'
    Process = 'com.tencent.mm:sandbox'

    def __init__(self, app):
        super(WXCancelUpdateConfirmDialog, self).__init__(app)
        self.update_locator({
            '标题': {'type': TextView, 'root': self, 'locator': QPath('/Text="提示"')},
            '否': {'type': Button, 'root': self, 'locator': QPath('/Text="否"')},
            '是': {'type': Button, 'root': self, 'locator': QPath('/Text="是"')},
        })

    def close(self):
        self.Controls['是'].click()
