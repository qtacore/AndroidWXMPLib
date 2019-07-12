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

'''登录相关界面
'''

import time

from qt4a.andrcontrols import Window, Button, EditText, TextView, ControlNotFoundError
from qt4a.qpath import QPath
from .util import MultiWindow


class LauncherPanel(MultiWindow):
    '''登录面板
    '''
    Activity = 'com.tencent.mm.plugin.account.ui.WelcomeActivity'
    Activity2 = 'com.tencent.mm.ui.LauncherUI'

    def __init__(self, wxapp):
        super(LauncherPanel, self).__init__(wxapp)
        self.update_locator({'注册': {'type': Button, 'root': self, 'locator': QPath('/Text="注册"')},
                            '登录': {'type': Button, 'root': self, 'locator': QPath('/Text="登录"')},
                            })

    def enter_login(self):
        '''点击登录进入登录面板
        '''
        self.Controls['登录'].wait_for_exist(20)
        self.Controls['登录'].click()


class LoginBasePanel(MultiWindow):
    Activity = 'com.tencent.mm.ui.account.mobile.MobileInputUI'
    Activity2 = 'com.tencent.mm.plugin.account.ui.MobileInputUI'
     
         
class LoginTypePanel(LoginBasePanel):
    '''登录面板
    '''

    def __init__(self, weixinapp):
        super(LoginTypePanel, self).__init__(weixinapp)
        self.update_locator({'用微信号/QQ号/邮箱登录': {'type': Button, 'root': self, 'locator': QPath('/Text="用微信号/QQ号/邮箱登录"')},
                            })

    def login_by_other(self):
        '''用微信号/QQ号/邮箱登录登录
        '''
        self.Controls['用微信号/QQ号/邮箱登录'].click()

class LoginPanel(LoginBasePanel):
    '''登录面板
    '''
    Activity = 'com.tencent.mm.ui.account.LoginUI'
    Activity2 = 'com.tencent.mm.plugin.account.ui.LoginUI'

    def __init__(self, weixinapp):
        super(LoginPanel, self).__init__(weixinapp)
        self.update_locator({'帐号': {'type': EditText, 'root': self, 'locator': QPath('/Type="MMClearEditText" && Visible="True" && Instance=0' )},
                            '密码': {'type': EditText, 'root': self, 'locator': QPath('/Type="MMClearEditText" && Visible="True" && Instance=-1')},
                            '登录': {'type': Button, 'root': self, 'locator': QPath('/Text="登录"')},
                            '否': {'type': TextView, 'root': self, 'locator': QPath('/Text="否"')}, #不看通讯录谁在用微信
                            })
        

    def login(self, account):
        '''帐号密码登录
        '''
        self.Controls['帐号'].disable_soft_input() #禁用软键盘
        self.Controls['帐号'].text = account.wxid
        self.Controls['密码'].text = account.password
        self.Controls['登录'].click()


class ReLoginPanel(LoginPanel):
    '''重新登录界面
    '''

    Activity = 'com.tencent.mm.plugin.account.ui.LoginPasswordUI'

    def __init__(self, weixinapp):
        super(ReLoginPanel, self).__init__(weixinapp)
    
    def login(self, account):
        '''帐号密码登录
        '''
        self.Controls['密码'].text = account.password
        self.Controls['登录'].click()