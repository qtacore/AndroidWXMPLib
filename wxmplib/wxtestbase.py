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

'''Android 微信测试基类
'''

import datetime
import os
import re
import shutil
import time

from qt4a.androidtestbase import AndroidTestBase
from qt4a.device import Device
from qt4a.androiddriver.util import logger


class WxTestBase(AndroidTestBase):
    '''微信测试基类
    '''
    
    def init_test(self, testresult):
        '''测试用例初始化
        '''
        super(WxTestBase, self).init_test(testresult)
    
    def post_test(self):
        '''清理测试用例
        '''
        logger.info('postTest run')
        super(WxTestBase, self).post_test()  
        logger.info('postTest complete')
  
    def acquire_device(self, type='Android', device_id='', **kwds):
        '''申请设备
        
        :param type: 申请的设备类型，目前尚未使用
        :type type:  string
        :param device_id: 申请的设备ID，默认不指定设备ID
        :type device_id:  string
        '''
        device = super(WxTestBase, self).acquire_device(device_id, **kwds)
        device.adb.start_logcat([])
        return device

    def extract_crash_by_patterns(self):  
        """
            #用户定义的crash规则
            @return: 返回规则列表
        """
        
        self._target_crash_proc_list = [r'com\.tencent\.mm.*']  # 要提取crash，必须对该变量赋值你所关心的进程，用正则表达式,关心多个应用则写多个正则

        # pattern_list中的每一个元素是一个二元组(tag_regex, content_regex)。
        # 例如日志"[com.tencent.mobileqq(21679)] [2017-01-04 15:44:30.516] E/crash(21679): com.tencent.mobileqq has crashed."
        # 中tag="crash", content="com.tencent.mobileqq has crashed.",这2个标签都支持正则，
        # 所以可以例如写为pattern_list.append((r".*", r'.*com\.tencent\.mobileqq.* has crashed\.'))。
        pattern_list = []                           
        pattern_list.append((r'.*', r'native crash happen'))  # 1.native_crash_key_single
        pattern_list.append((r'native_eup', r'crash happen at.*'))  # 2.native_crash_key_first
        pattern_list.append((r'.*', r'.*com\.tencent\.mm.* has crashed\.'))  # 3.java_crash_key_single
        pattern_list.append((r'CrashAnrDetector', r'.*com\.tencent\.mm.*'))  # 4.video_crash_key_single
        pattern_list.append((r'StatisticCollector', r'getCrashExtraMessage...isNativeCrashed:.*'))
  
        return pattern_list
 
