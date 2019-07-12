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

'''小程序相关界面
'''

import re
import time
from tuia.exceptions import ControlNotFoundError
from qt4w import XPath
from qt4w.webcontrols import WebPage, WebElement, ui_list
from qt4a.qpath import QPath
from qt4a.andrcontrols import Button, EditText, FrameLayout, ImageButton, RecyclerView, TextView, View, Window
from qt4a.androiddriver.util import logger, general_encode
from .util import MiniProgramWebView, WXBrowserPanel, TBSDownloadDialog, NoScrollListView


class MiniProgramLauncherPanel(Window):
    '''小程序启动面板
    '''
    Activity = 'com.tencent.mm.plugin.appbrand.ui.AppBrandLauncherUI'

    def __init__(self, app):
        super(MiniProgramLauncherPanel, self).__init__(app)
        self.update_locator({'搜索': {'type': ImageButton, 'root': self, 'locator': QPath('/Desc="搜索"')},
                             'FrameLayout': {'type': FrameLayout, 'root': self, 'locator': QPath('/Id="content" /Type="FrameLayout" && MaxDepth=2 /Type="FrameLayout"')},
                             '小程序列表1': {'type': NoScrollListView, 'root': self, 'locator': QPath(r'/Type~="AppBrandLauncherRecentsList\$\d+"')},
                             '小程序列表2': {'type': NoScrollListView, 'root': '@FrameLayout', 'locator': QPath('/Instance=0')},
                             '小程序名称': {'type': TextView, 'root': '@小程序列表', 'locator': QPath('/Type="LinearLayout" /Type="TextView" && Visible="True"')},
                             })

    def __getitem__(self, index):
        if index == '小程序列表':
            if self.Controls['小程序列表1'].exist():
                return self.Controls['小程序列表1']
            else:
                return self.Controls['小程序列表2']
        else:
            return super(MiniProgramLauncherPanel, self).__getitem__(index)

    def open_app(self, app_name, force_by_search=False):
        '''打开小程序
        '''
        found = False
        if not force_by_search:
            timeout = 2
            time0 = time.time()
            while time.time() - time0 < timeout:
                if len(self.Controls["小程序列表"]) > 2:
                    break
                time.sleep(0.5)

            for i in range(3):
                logger.info('第%d次尝试查找小程序' % i)
                for i in range(1, len(self.Controls["小程序列表"])):
                    it = self.Controls["小程序列表"][i]
                    if it.has('小程序名称'):
                        if general_encode(it['小程序名称'].text) == general_encode(app_name):
                            it.click()
                            found = True
                            break
                if found:
                    break
                time.sleep(1)
        if not found:
            # 通过搜索进入
            self.Controls["搜索"].click()
            search_panel = MiniProgramSearchPanel(self)
            search_panel.open_app(app_name)

        try:
            self._app.wait_for_activity(TBSDownloadDialog.Activity)
        except:
            pass
        else:
            dialog = TBSDownloadDialog(self)
            if dialog.exist():
                dialog.upgrade()
            time.sleep(4)

        app_panel = MiniProgramPanel(self)
        try:
            app_panel.wait_for_exist()
        except ControlNotFoundError:
            return self.open_app(app_name)
        else:
            return app_panel


class MiniProgramSearchPanel(WXBrowserPanel):
    '''小程序搜索界面
    '''
    Activity = 'com.tencent.mm.plugin.appbrand.ui.AppBrandSearchUI'

    def __init__(self, app):
        super(MiniProgramSearchPanel, self).__init__(app)
        self.update_locator({'搜索框': {'type': EditText, 'root': self, 'locator': QPath('/Type="EditText"')},
                             })

    def open_app(self, app_name):
        '''搜索并打开小程序
        '''
        self.Controls["搜索框"].text = app_name
        search_page = MiniProgramSearchPage(self.Controls["webview"])
        search_page.open_app(app_name)


class MiniProgramSearchPage(WebPage):
    '''小程序搜索结果页面
    '''
    ui_map = {'推荐搜索列表': {'type': ui_list(WebElement),
                         'locator': XPath('//div[@class="sug_wrp"]/div[@class="weui_cells"]/div[@class="weui_cell"]'),
                         'ui_map': {
        '小程序名': XPath('//p[@class="sug_text"]')
    }
    },
        '使用过的小程序列表': {'type': ui_list(WebElement),
                      'locator': XPath('//div[@class="weui_cells"]/div[@class="weui_cell search_item sug_biz"]'),
                      'ui_map': {'小程序名': XPath('//em[@class="highlight"]')
                                 }
                      },
        '搜索历史列表': {
        'type': ui_list(WebElement),
        'locator': XPath('//div[@class="history_page"]/div[@class="weui_cells"]'),
        'ui_map': {
            '小程序名': XPath('//p[@class="history_text"]')
        }
    },
        '小程序列表': {'type': ui_list(WebElement),
                  'locator': XPath('//ul[@class="search_list"]/div/li'),
                  'ui_map': {'小程序名': XPath('//h3[@class="search_item_title"]/em[@class="highlight"]')
                             }
                  }
    }

    def open_app(self, app_name):
        '''进入小程序
        '''
        # time.sleep(1)
        if len(self.control('推荐搜索列表')) > 0:
            for it in self.control('推荐搜索列表'):
                if it.control('小程序名').inner_text.upper() == app_name.upper():
                    it.click()
                    break
        elif len(self.control('搜索历史列表')) > 0:
            for it in self.control('搜索历史列表'):
                if it.control('小程序名').inner_text.upper() == app_name.upper():
                    it.click()
                    break

        timeout = 5
        time0 = time.time()
        while time.time() - time0 < timeout:
            if len(self.control('小程序列表')) > 0:
                break
            time.sleep(0.2)
        else:
            raise RuntimeError('未搜索到小程序')

        for it in self.control('小程序列表'):
            if it.control('小程序名').inner_text.upper() == app_name.upper():
                it.click()
                return
        else:
            raise RuntimeError('小程序：%s 不存在' % app_name)

        for it in self.control('使用过的小程序列表'):
            if it.control('小程序名').inner_text.upper() == app_name.upper():
                it.click()
                return
        else:
            raise RuntimeError('搜索结果中未找到小程序：%s' % app_name)


class MiniProgramPanel(WXBrowserPanel):
    '''小程序界面
    '''
    Activity = 'com.tencent.mm.plugin.appbrand.ui.AppBrandInToolsUI'
    Activity2 = r'com.tencent.mm.plugin.appbrand.ui.AppBrandUI(\d*)'
    Process = 'com.tencent.mm:tools'  # toolsmp
    Process2 = r'com.tencent.mm:appbrand%s'

    def __init__(self, app):
        super(MiniProgramPanel, self).__init__(app)
        self.update_locator({'标题': {'type': TextView, 'root': self, 'locator': QPath('/Type="RelativeLayout" /Type="RelativeLayout" /Type="LinearLayout" /Type="TextView" && Visible="True"')},
                             '菜单': {'type': ImageButton, 'root': self, 'locator': QPath('/Type="AppBrandOptionButton" /Type="ImageButton" && Visible="True"')},
                             '返回': {'type': ImageButton, 'root': self, 'locator': QPath('/Type="AppBrandCapsuleHomeButton" /Type="ImageButton" && Visible="True"')},
                             '加载中': {'type': View, 'root': self, 'locator': QPath('/Type="ThreeDotsLoadingView"')},
                             })
        self._wait_for_window = True  # 是否等待窗口标题变化

        # for key in self._locators:
        #     if self._locators[key]['type'].__name__.endswith('WebView'):
        #         self._locators[key]['type'] = MiniProgramWebView(self._locators[key]['type'])

    def post_init(self):
        # time.sleep(20) #过早注入会crash，无法判断webview是否加载完成，待优化
        timeout = 60
        time0 = time.time()
        while time.time() - time0 < timeout:
            if self.Controls["加载中"].exist() and self.Controls["加载中"].visible:
                time.sleep(1)
            else:
                break
        else:
            raise RuntimeError('小程序加载失败')
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

    def wait_for_exist(self, timeout=10, interval=0.5):
        '''等待窗口出现
                处理窗口名和进程名会变的问题
        '''
        time0 = time.time()
        current_activity = ''
        pattern = re.compile(self.__class__.Activity2)
        while time.time() - time0 < timeout:
            current_activity = self.device.get_current_activity()
            if current_activity == self.__class__.Activity:
                return True
            if current_activity:
                ret = pattern.match(current_activity)
                if ret:
                    if ret.group(1):
                        process = self.Process2 % ret.group(1)
                    else:
                        process = self.Process2 % 0
                    self._driver = self._app.get_driver(process)
                    for key in self._locators:
                        # 替换掉_driver实例
                        self._locators[key]['activity'] = current_activity
                        self._locators[key]['driver'] = self._driver

                    return True
            time.sleep(interval)
        raise ControlNotFoundError('窗口：%s 未找到，当前窗口为：%s' % (
            self.__class__.Activity, current_activity))

    def close(self):
        '''关闭
        '''
        self.Controls["返回"].click()


class WXMPPage(WebPage):
    '''小程序页面基类
    '''

    def __init__(self, wxapp):
        mppanel = MiniProgramPanel(wxapp)
        webview = mppanel.Controls['webview']
        super(WXMPPage, self).__init__(webview)


class AuthorizationDialog(MiniProgramPanel):
    '''授权弹窗
    '''

    def __init__(self, app):
        super(AuthorizationDialog, self).__init__(app)
        self.update_locator({
            '允许': {'type': Button, 'root': self, 'locator': QPath('/Text="允许"')},
            '拒绝': {'type': Button, 'root': self, 'locator': QPath('/Text="拒绝"')},
        })
    
    def close(self):
        self.Controls['允许'].click()
