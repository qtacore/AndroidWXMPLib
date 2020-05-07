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
'''主界面
'''

import hashlib
import time
import os

from PIL import Image

from qt4a.andrcontrols import Window, ListView, TextView, Button, ActionMenuItemView, ImageView
from qt4a.qpath import QPath
from qt4a.androiddriver.util import logger, general_encode

from .album import AlbumPreviewPanel
from .login import ExtDeviceLoginPanel


class MainPanel(Window):
    '''主面板
    '''
    Activity = 'com.tencent.mm.ui.LauncherUI'

    def __init__(self, wxapp):
        super(MainPanel, self).__init__(wxapp)
        self.update_locator({
            '左上角微信': {
                'type': TextView,
                'root': self,
                'locator': QPath('/Type="RelativeLayout" /Id="text1" && Visible="True"')
            },
            '搜索': {
                'type': ActionMenuItemView,
                'root': self,
                'locator': QPath('/Desc="搜索"')
            },
            '更多': {
                'type': ImageView,
                'root': self,
                'locator': QPath('/Type="AppBrandDesktopContainer" /Type="FrameLayout" && MaxDepth=2 /Type="RelativeLayout" && MaxDepth=3 && Instance=1 /Type="ImageView" && Visible="True"')
            },
            '发现': {
                'type': TextView,
                'root': self,
                'locator': QPath('/Text="发现"')
            },
        })

    def wait_for_recv_message(self, timeout=120, interval=0.5):
        '''等待接收消息完成
        '''
        from tuia.exceptions import ControlNotFoundError
        time0 = time.time()
        recving = self.Controls['左上角微信']
        try:
            recving.wait_for_exist(20, 0.5)
        except ControlNotFoundError:
            logger.warn('wait for loading timeout')

        while time.time() - time0 < timeout:
            if not recving.exist() or not recving.visible:
                time.sleep(2)
                continue
            if '(' not in self.Controls['左上角微信'].text:
                time.sleep(1)
                continue
            break
        old_text = self.Controls['左上角微信'].text
        time0 = time.time()
        while time.time() - time0 < 5:
            time.sleep(2)
            new_text = self.Controls['左上角微信'].text
            if new_text != old_text:
                old_text = new_text
                time.sleep(3)
            else:
                break

    def open_url(self, url, activity=None, **kwds):
        '''使用内置浏览器打开URL
        
        :param url: 要打开的url地址
        :type url:  string
        :param activity: 
        :type activity:
        '''
        if not activity:
            activity = 'com.tencent.mm.plugin.webview.ui.tools.WebViewUI'
        activity = '%s/%s' % (self._app.package_name, activity)
        extra = {
            'rawUrl': url,
        }
        if kwds: extra.update(kwds)
        self.device.start_activity(activity, extra=extra)
        self._app.wait_for_activity(activity.split('/')[1], 10)

    def open_discover_tab(self):
        '''打开“发现”tab页
        '''
        self.Controls["发现"].click()
        return DiscoverPanel(self)

    def scan_image(self, image_path, use_camera=False):
        '''扫描图片
        '''
        if not os.path.exists(image_path):
            raise RuntimeError('Image file %s not exist' % image_path)

        with open(image_path, 'rb') as fp:
            image_data = fp.read()
        image_hash = hashlib.md5(image_data).hexdigest()
        if use_camera:
            if not self.device.is_emulator_device():
                raise RuntimeError('Only emulator supported')
            if not image_path.endswith('.bmp'):
                image = Image.open(image_path).convert("RGB")
                size = image.size
                if size[0] < 480:
                    width = 480
                    height = 480 * size[1] / size[0]
                    image = image.resize((width, height))
                image_path += '.bmp'
                image.save(image_path)
            save_path = '/data/local/tmp/%s.bmp' % image_hash
            self.device.push_file(image_path, save_path)
            self.device.adb.set_property('qemu.sf.fake_camera.input_path', save_path)
        else:
            save_path = '/sdcard/dcim/%s%s' % (image_hash, os.path.splitext(image_path)[-1])
            self.device.push_file(image_path, save_path)
            self.device.refresh_media_store(save_path)
            
        self.Controls['更多'].click()
        popup_menu = PopupMenu(self)
        popup_menu.Controls['扫一扫'].click()
        scan_panel = ScanPanel(self)
        if not use_camera:
            scan_panel.open_album()
            preview_panel = AlbumPreviewPanel(self)
            preview_panel.select_image('dcim')

        scan_panel.wait_for_open()


class PopupMenu(Window):
    '''弹出菜单
    '''
    Activity = r'PopupWindow:\w+'

    def __init__(self, app):
        super(PopupMenu, self).__init__(app)
        self.update_locator({
            '扫一扫': {
                'type': TextView,
                'root': self,
                'locator': QPath('/Text="扫一扫"')
            }
        })


class ScanPanel(Window):
    '''扫一扫界面
    '''
    Activity = 'com.tencent.mm.plugin.scanner.ui.BaseScanUI'

    def __init__(self, app):
        super(ScanPanel, self).__init__(app)
        self.update_locator({
            '更多': {
                'type': ImageView,
                'root': self,
                'locator': QPath('/Type="ActionMenuView" /Type="ImageButton" && Visible="True" && MaxDepth=4')
            },
            '相册': {
                'type': ImageView,
                'root': self,
                'locator': QPath('/Type="ScanSharedMaskView" /Type="WeImageView" && Visible="True" && MaxDepth=3')
            },
            '扫描完成': {
                'type': TextView,
                'root': self,
                'locator': QPath('/Text="扫描完成\n正在准备打开"')
            }
        })
        

    def open_album(self):
        '''打开相册
        '''
        if self.Controls['相册'].exist():
            self.Controls['相册'].click()
        elif self.Controls['更2'].exist():
            self.Controls['更多'].click()
            popup_dialog = ScanPopupDialog(self)
            popup_dialog.Controls['从相册选取二维码'].click()

    def wait_for_open(self, timeout=30):
        '''等待打开
        '''
        time0 = time.time()
        while time.time() -time0 < timeout:
            if self.Controls['扫描完成'].exist() and self.Controls['扫描完成'].visible:
                time.sleep(0.5)
            else:
                break
        else:
            raise RuntimeError('扫描图片失败')

        while time.time() - time0 < timeout:
            activity = self.device.current_activity
            if activity == self.Activity:
                time.sleep(1)
            elif activity == ExtDeviceLoginPanel.Activity:
                panel = ExtDeviceLoginPanel(self)
                panel.login()
                return
            else:
                return


class ScanPopupDialog(Window):
    '''扫一扫弹窗
    '''
    Activity = 'com.tencent.mm.plugin.scanner.ui.BaseScanUI'

    def __init__(self, app):
        super(ScanPopupDialog, self).__init__(app)
        self.update_locator({
            '从相册选取二维码': {
                'type': TextView,
                'root': self,
                'locator': QPath('/Text="从相册选取二维码"')
            }
        })

class PrivacyDialog(Window):
    '''隐私对话框
    '''
    Activity = 'com.tencent.mm.ui.LauncherUI'

    def __init__(self, app):
        super(PrivacyDialog, self).__init__(app)
        self.update_locator({
            '了解更多': {
                'type': Button,
                'root': self,
                'locator': QPath('/Text="了解更多"')
            },
        })

    def exist(self):
        '''该窗口是否存在
        '''
        return self.Controls['了解更多'].exist()

    def close(self):
        self.Controls['了解更多'].click()
        agree_panel = PrivacyAgreementPanel(self)
        agree_panel.agree()


class PrivacyAgreementPanel(Window):
    '''微信隐私保护指引
    '''
    Activity = 'com.tencent.mm.ui.account.ShowAgreementsUI'
    Process = 'com.tencent.mm:tools'

    def __init__(self, app):
        super(PrivacyAgreementPanel, self).__init__(app)
        self.update_locator({
            '同意': {
                'type': TextView,
                'root': self,
                'locator': QPath('/Text="同意"')
            },
        })

    def agree(self):
        self.Controls['同意'].click()


class DiscoverPanel(MainPanel):
    '''发现面板
    '''

    def __init__(self, app):
        super(DiscoverPanel, self).__init__(app)
        self.update_locator({
            '入口列表': {
                'type': ListView,
                'root': self,
                'locator': QPath('/Id="list" && Instance=0')
            },
            '入口名': {
                'type': TextView,
                'root': '@入口列表',
                'locator': QPath('/Type="LinearLayout" /Id="title"')
            },
            #'小程序': {'type': TextView, 'root': '@入口列表', 'locator': QPath('/Text="小程序"')},
        })

    def __getitem__(self, name):
        '''支持不定义控件自动查找，并滑动到可见
        '''
        try:
            return super(DiscoverPanel, self).__getitem__(name)
        except NameError:
            for i in range(len(self.Controls["入口列表"])):
                it = self.Controls["入口列表"][i]
                if it.has('入口名') and general_encode(
                        it['入口名'].text) == general_encode(name):
                    return it['入口名']
            else:
                raise

    def open_mini_program(self, app_name):
        '''打开小程序
        '''
        from .mini_program import MiniProgramLauncherPanel
        self.Controls["小程序"].click()
        launcher_panel = MiniProgramLauncherPanel(self)
        time.sleep(1)
        return launcher_panel.open_app(app_name)
