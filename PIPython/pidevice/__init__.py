#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Collection of libraries to use PI controllers and process GCS data."""

from . import gcserror
from .gcserror import GCSError
from .gcs2.gcs2commands import GCS2Commands
from .gcs2.gcs2device import GCS2Device
from .gcs30.gcs30commands import GCS30Commands
from .gcs30.gcs30device import GCS30Device
from .gcs30.gcs30commands_helpers import isgcs30
from .gcs30.gcs30error import GCS30Error
from .gcsdevice import GCSDevice

__all__ = ['GCSDevice', 'GCS2Device', 'GCS30Device', 'GCS2Commands', 'GCS30Commands', 'isgcs30']

__signature__ = 0xb95fbfed9f30a0eb1dcfb34eca5dd938
