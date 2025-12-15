#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoQuant - 策略模块
"""

from .base import BaseStrategy
from .ma_cross import DoubleMaStrategy

__all__ = [
    "BaseStrategy",
    "DoubleMaStrategy",
]
