#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoQuant - 数据加载模块
"""

from .loader import generate_dummy_data
from .realistic_dummy import generate_realistic_btc_data

__all__ = [
    "generate_dummy_data",
    "generate_realistic_btc_data",
]
