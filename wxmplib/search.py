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

'''搜索面板
'''

from qt4a.qpath import QPath
from qt4a.andrcontrols import Window
from .util import ActionBarEditText

class SearchPanel(Window):
    '''搜索面板
    '''
    
    def __init__(self, app):
        super(SearchPanel, self).__init__(app)
        self.updateLocator({'搜索框': {'type': ActionBarEditText, 'root': self, 'locator': QPath('/Type="ActionBarSearchView$ActionBarEditText"')},
                            
                            })
