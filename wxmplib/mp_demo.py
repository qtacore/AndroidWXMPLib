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

from qt4w import XPath
from qt4w.webcontrols import WebElement, ui_list
from qt4a.androiddriver.util import logger

from .mini_program import WXMPPage


class MiniProgramComponentPage(WXMPPage):
    '''微信官方小程序示例主页面
    '''
    ui_map = {
        '视图容器区域': {
            'type': WebElement,
            'locator': XPath('//wx-view[@class="kind-list-item"][1]'),
            'ui_map': {
                '标题': XPath('//*[@id="view"]'),
                'view': XPath('//*[text()="view"]'),
                'scroll-view': XPath('//*[text()="scroll-view"]')
            }
        },
        '组件分类': {
            'type': ui_list(WebElement),
            'locator': XPath('//wx-view[@class="kind-list-item"]'),
            'ui_map': {
                '标题': XPath('//wx-view[@class="kind-list-text"]'),
                '组件列表': {
                    'type': ui_list(WebElement),
                    'locator': XPath('//wx-navigator[@class="navigator"]'),
                    'ui_map': {
                        '名称': XPath('/wx-view[@class="navigator-text"]')
                    }
                }
            }
        }
     }


    def open_component_page(self, category, name):
        '''打开组件页面
        '''
        for cat in self.control('组件分类'):
            if cat.control('标题').inner_text == category:
                rect1 = cat.rect
                rect2 = cat.control('标题').rect
                if rect1[3] - rect2[3] < 200:
                    # 需要展开
                    cat.click()
                for comp in cat.control('组件列表'):
                    if comp.control('名称').inner_text == name:
                        comp.click()
                        return
                else:
                    raise RuntimeError('Find component %s failed' % name)
        else:
            raise RuntimeError('Find component type %s failed' % category)



class MiniProgramTextPage(WXMPPage):
    '''小程序text组件界面
    '''
    ui_map = {
        '文本区域': XPath('//wx-text/span[2]'),
        '添加一行': XPath('//wx-button[text()="add line"]'),
        '移除一行': XPath('//wx-button[text()="remove line"]')
    }

    def add_line(self):
        self.control('添加一行').click()
    
    def remove_line(self):
        self.control('移除一行').click()
