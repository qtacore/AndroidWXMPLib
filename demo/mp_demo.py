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

'''小程序demo
'''

import time
import os

from qt4a.device import Device
from wxmplib.account import WeiXinAccount
from wxmplib.wxapp import WeiXinApp
from wxmplib.mini_program import MiniProgramPanel
from wxmplib.mp_demo import MiniProgramComponentPage, MiniProgramTextPage


def open_mp_demo(wxid, password):
    device = Device()
    wxacc = WeiXinAccount(wxid, password)
    wxapp = WeiXinApp(device)
    wxapp.login(wxacc)
    page = wxapp.open_mini_program('小程序示例', MiniProgramComponentPage)
    page.open_component_page('基础内容', 'text')
    time.sleep(2)

    page = MiniProgramTextPage(wxapp)
    page.add_line()
    page.add_line()
    page.add_line()
    page.add_line()
    print(page.control('文本区域').inner_text)

if __name__ == '__main__':
    open_mp_demo(os.environ['WX_ID'], os.environ['WX_PASSWORD'])
    
    