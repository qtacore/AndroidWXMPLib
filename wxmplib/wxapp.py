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

'''Android 微信 app
'''

import time
import xml.dom.minidom

from qt4a.androidapp import AndroidApp
from qt4a.androiddriver.util import logger, TimeoutError
from tuia.exceptions import ControlNotFoundError

from .login import LauncherPanel, LoginTypePanel, LoginPanel, ReLoginPanel
from .main import MainPanel, PrivacyDialog
from .mini_program import WXMPPage
from .util import WXUpdateDialog

class WeiXinApp(AndroidApp):
    '''安卓微信 App类
    '''
    # 包名
    package_name = 'com.tencent.mm'
    # 启动手Q的activity名
    startup_activity = 'com.tencent.mm/.ui.LauncherUI'
    
    def __init__(self, device, clear_state=False, debug=False):
        '''
        :param device: 设备实例
        :type device:  Device
        :param clear_state: 是否清登录态，默认为True
        :type  clear_state: bool
        '''
        super(WeiXinApp, self).__init__(self.package_name, device, not debug)
        self._clear_state = clear_state
        if self._clear_state:
            self._start(True, True)

    def resume(self):
        '''当微信被切换到后台时，重新将微信唤醒
        '''
        self.device.adb.start_activity(self.startup_activity)
        
    def _start(self, clear_state=True, kill_process=True, start_extra_params={}):
        '''启动Android微信
        '''
        
        if kill_process == True:
            self.device.kill_process(self.package_name)  # 杀死已有进程
            
        if clear_state == True:
            # 清登录态，不清数据
            logger.warn('Clearing user state')
            self.run_shell_cmd('rm /data/data/%s/shared_prefs/%s*.xml' % (self.package_name, self.package_name))
            self.run_shell_cmd('rm /data/data/%s/MicroMsg/*.cfg' % (self.package_name))
            self.run_shell_cmd('rm /data/data/%s/shared_prefs/system_config_prefs.xml' % (self.package_name))
            
        # try:
        #     # 目前还不支持xwalk内核，先强制不使用该内核
        #     self.run_shell_cmd('rm -r /data/data/%s/app_xwalkconfig' % (self.package_name))
        #     self.run_shell_cmd('touch /data/data/%s/app_xwalkconfig' % (self.package_name))
        #     self.run_shell_cmd('chmod 777 /data/data/%s/app_xwalkconfig' % (self.package_name))
        #     self.run_shell_cmd('rm -r /data/data/%s/app_xwalk_*' % (self.package_name))
        # except:
        #     logger.exception('Disable xwalk failed')
            
        try:
            self.device.start_activity(self.startup_activity, extra=start_extra_params) 
        except TimeoutError:
            logger.exception('Start Android Wechat Failed')
            self.device.clear_data(self.package_name)
            self.device.start_activity(self.startup_activity, extra=start_extra_params)
    
    def get_login_user(self):
        '''获取当前登录用户
        '''
        result = self.run_shell_cmd('cat /data/data/%s/shared_prefs/%s_preferences.xml' % (self.package_name, self.package_name))
        try:
            dom = xml.dom.minidom.parseString(result)
        except:
            return None

        for it in dom.documentElement.getElementsByTagName('boolean'):
            if it.getAttribute('name') == 'isLogin':
                if it.getAttribute('value') != 'true': return None # 当前没有登录用户
                break
                
        for it in dom.documentElement.getElementsByTagName('string'):
            if it.getAttribute('name') == 'login_user_name':
                return it.childNodes[0].nodeValue
                
        logger.error(result)
        return None
    
    def disable_popup_window(self):
        self.set_activity_popup(WXUpdateDialog.Activity) # 禁用微信升级弹窗
        self.set_activity_popup('com.tencent.mm.sandbox.updater.AppUpdaterUI')

    def login(self, account, timeout=10):
        '''登录微信
        
        :param account: 微信账户
        :type  account: WeiXinAccount
        '''
        if not self._clear_state:
            login_user = self.get_login_user()
            if not login_user:
                logger.info('Current user is %s' % login_user)
            if login_user == account.wxid:
                # 已经是当前用户
                logger.info('WeiXin account %s is logged in' % login_user)
                self._start(False, True)
                self.disable_popup_window()
                try:
                    self.wait_for_activity(ReLoginPanel.Activity, 10)
                except ControlNotFoundError:
                    return
                else:
                    # 需要登录
                    login_panel = ReLoginPanel(self)
                    login_panel.login(account)

                try:
                    self.wait_for_activity(WXUpdateDialog.Activity, 10)
                except ControlNotFoundError:
                    return
                else:
                    # 这种情况下使用接口禁用弹窗很难保证顺序，因此使用点击方法处理
                    update_dialog = WXUpdateDialog(self)
                    update_dialog.close()
                return
        self._start(True, True) # 清登录态并启动微信

        launch_panel = LauncherPanel(self)
        launch_panel.enter_login()
        
        self.disable_popup_window()

        login_type_panel = LoginTypePanel(self)
        login_type_panel.login_by_other()
        
        login_panel = LoginPanel(self)
        login_panel.login(account)
        time0 = time.time()
        timeout = 40
        while time.time() - time0 < timeout:
            current_activity = self.device.current_activity
            if current_activity == LoginPanel.Activity or current_activity == LoginPanel.Activity2:
                if login_panel.Controls['否'].exist() and login_panel.Controls['否'].visible:
                    login_panel.Controls['否'].click()
            elif current_activity == MainPanel.Activity:
                break
            else:
                time.sleep(2)

        main_panel = MainPanel(self)
        main_panel.wait_for_recv_message()
        privacy_dialog = PrivacyDialog(self)
        if privacy_dialog.exist():
            privacy_dialog.close()
    
    def open_mini_program(self, app_name, wxmp_page_cls=None):
        '''启动微信小程序
        '''
        main_panel = MainPanel(self)
        discover_panel = main_panel.open_discover_tab()
        time.sleep(2)
        discover_panel.open_mini_program(app_name)
        if not wxmp_page_cls:
            wxmp_page_cls = WXMPPage
        return wxmp_page_cls(self)
        
    
