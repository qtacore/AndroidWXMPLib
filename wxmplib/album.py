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
'''相册界面
'''

import time

from qt4a.andrcontrols import Window, GridView, ListView, TextView, RecyclerView
from qt4a.qpath import QPath

from .util import NoScrollListView


class AlbumPreviewPanel(Window):
    '''相册预览窗口
    '''
    Activity = 'com.tencent.mm.plugin.gallery.ui.AlbumPreviewUI'
    Process1 = 'com.tencent.mm:tools'

    def __init__(self, app):
        super(AlbumPreviewPanel, self).__init__(app)
        self.update_locator({
            '所有图片': {
                'type': TextView,
                'root': self,
                'locator': QPath('/Text="所有图片"')
            },
            '图片列表1': {
                'type': GridView,
                'root': self,
                'locator': QPath('/Type="GridView"')
            },
            '图片列表2': {
                'type': NoScrollListView,
                'root': self,
                'locator': QPath('/Type="RecyclerView"')
            },
        })

    def post_init(self):
        time.sleep(2) # 等待窗口初始化
        if not self.Controls['所有图片'].exist():
            self.Process = self.__class__.Process1
            self._driver = self._app.get_driver(self.__class__.Process1)

    def select_image(self, album_name, image_name=None):
        '''选择图片
        '''
        if self.Process == self.__class__.Process1:
            self.Controls['所有图片'].click()
            album_dialog = AlbumListDialog(self)
            album_dialog.select_album(album_name)
            time.sleep(1) # 等待图片列表更新
            self.Controls['图片列表1'][0].click()
        else:
            self.Controls['图片列表2'][1].click()


class AlbumListDialog(Window):
    '''相册列表弹窗
    '''
    Activity = 'com.tencent.mm.plugin.gallery.ui.AlbumPreviewUI'
    Process = 'com.tencent.mm:tools'

    def __init__(self, app):
        super(AlbumListDialog, self).__init__(app)
        self.update_locator({
            '相册列表': {
                'type': ListView,
                'root': self,
                'locator': QPath('/Type="ListView"')
            },
            '相册名': {
                'type': TextView,
                'root': '@相册列表',
                'locator': QPath('/Type="LinearLayout" /Type="TextView" && Instance=0')
            }
        })

    def select_album(self, album_name):
        '''选择相册
        '''
        for it in self.Controls['相册列表']:
            if it['相册名'].text.lower() == album_name.lower():
                it.click()
                return
        else:
            raise RuntimeError('Album %s not found' % album_name)


