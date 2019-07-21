# -*- coding: utf-8 -*-

"""
Display keyboard layout in sway

Configuration parameters:
    ids: if list is not empyt, only search for keyboards with their id in this
        list. Find the id of your keyboards using "swaymsg -t get_inputs -r".
        (default [])
    top: restrict the number of displayed keyboards to this number. If the
        parameter "ids" is set, the order of "ids" determines priority. Set
        this number to 0 to disable the restriction.
        (default 1)
    format: string that formats the output. See placeholders below.
        (default '[⌨ {devices}]|\?color=bad ⌨')
    format_device: display format for each keyboard
        (default '\?color=darkgrey {name} [\?color=layout {layout}]')
    format_separator: text separator if more than one keyboard
        (default ', ')
    name_aliases: dictionary "id: name", overrides "name" placeholder
        (default {})
    layout_colors: dictionary "layout: color", associate colors to layouts.
        None is the key for unknown layouts.
        (default {None: 'bad'})
    layout_aliases: dictionary "layout: new_layout", overrides "layout"
        placeholder. None is the key for unknown layouts.
        (default {None: 'disc.'})
    display_no_data: display a keyboard even if layout/data is not found
        (default False)
    display_reverse: reverse display order of keyboards after all restrictions
        are applied
        (default False)
    swaymsg: path to swaymsg executable
        (default 'swaymsg')
    cache_timeout: refresh interval
        (default 10)

Format placeholders:
    {devices} formatted keyboard layouts

format_device placeholders:
    {id} input device id
    {name} Post-aliased keyboard name. If there is no alias or name is not
           detected, fallsback to id.
    {layout} Post-aliased keyboard name

Color options for format_device:
    layout: color associated to keyboard layout, as configured in layout_colors

Examples:
```
# Two keyboards, priority to internal
keyboard_layout {
    ids = ['1:1:Model_keyboard', '1234:56789:USB_Keyboard', '4321:55555:USB3_Keyboard']
    name_aliases = {
        '1:1:Model_keyboard': 'int',
        '1234:56789:USB_Keyboard': 'ext',
        '4321:55555:USB3_Keyboard': 'ext',
    }
    layout_colors = {
        None: 'bad',
        'Spanish': '#f0c674',
        'English (US)': '#0000ff',
    }
    layout_aliases = {
        None: 'disc.',
        'Spanish': 'es',
        'English (US)': 'us',
    }
    top = 2
    display_reverse = True
}

# Two keyboards, display even if usb disconnected
keyboard_layout {
    ids = ['1234:56789:USB_Keyboard', '1:1:Model_keyboard']
    name_aliases = {
        '1234:56789:USB_Keyboard': 'ext',
        '1:1:Model_keyboard': 'int',
    }
    layout_colors = {
        None: 'bad',
        'Spanish': '#f0c674',
        'English (US)': '#0000ff',
    }
    layout_aliases = {
        None: 'disc.',
        'Spanish': 'es',
        'English (US)': 'us',
    }
    top = 2
    display_no_data = True
}

# minimalistic, get layout of first keyboard available
keyboard_layout {
    ids = ['1234:56789:USB_Keyboard', '4321:55555:USB3_Keyboard', '1:1:Model_keyboard']
    layout_colors = {
        None: 'bad',
        'Spanish': '#f0c674',
        'English (US)': '#0000ff',
    }
    layout_aliases = {
        None: 'disc.',
        'Spanish': 'es',
        'English (US)': 'us',
    }
    top = 1,
    format_device = '\?color=layout {layout}'
}
```

@author javiertury

SAMPLE OUTPUT

[
    {'full_text': '⌨ ', 'separator': False, 'separator_block_width': 0},
    {'full_text': 'ext ', 'color': '#a9a9a9', 'separator': False, 'separator_block_width': 0},
    {'full_text': 'us', 'color': '#0000ff', 'separator': False, 'separator_block_width': 0},
    {'full_text': ', ', 'separator': False, 'separator_block_width': 0},
    {'full_text': 'int ', 'color': '#a9a9a9', 'separator': False, 'separator_block_width': 0},
    {'full_text': 'es', 'color': '#f0c674', 'separator': False, 'separator_block_width': 0}
]

two keyboards, usb disconnected
[
    {'full_text': '⌨ ', 'separator': False, 'separator_block_width': 0},
    {'full_text': 'ext ', 'color': '#a9a9a9', 'separator': False, 'separator_block_width': 0},
    {'full_text': 'disc.', 'color': 'bad', 'separator': False, 'separator_block_width': 0},
    {'full_text': ', ', 'separator': False, 'separator_block_width': 0},
    {'full_text': 'int ', 'color': '#a9a9a9', 'separator': False, 'separator_block_width': 0},
    {'full_text': 'es', 'color': '#f0c674', 'separator': False, 'separator_block_width': 0}
]

minimalistic
[
    {'full_text': '⌨ ', 'separator': False, 'separator_block_width': 0},
    {'full_text': 'us', 'color': '#0000ff', 'separator': False, 'separator_block_width': 0}
]
"""

import subprocess
import json


class Py3status:

    ids = []
    top = 1
    format = '[⌨ {devices}]|\?color=bad ⌨'
    format_device = '\?color=darkgrey {name} [\?color=layout {layout}]'
    format_separator = ', '
    name_aliases = {}
    layout_aliases = {None: 'disc.'}
    layout_colors = {None: 'bad'}
    display_no_data = False
    display_reverse = False
    swaymsg = 'swaymsg'
    cache_timeout = 10

    def keyboard_layout_sway(self):
        raw_info = subprocess.run([self.swaymsg, '-t', 'get_inputs', '-r'],
                                  stdout=subprocess.PIPE).stdout
        info = json.loads(raw_info)

        devices = {}
        for item in info:
            if item['type'] == 'keyboard' and \
                    'xkb_active_layout_name' in item:

                id = item['identifier']
                devices[id] = {
                    'id': id,
                    'layout': item['xkb_active_layout_name'],
                    'name': item['name'],
                }

        iterable_ids = self.ids if len(self.ids) else devices
        texts = []

        for id in iterable_ids:
            if (not self.display_no_data) and (id not in devices):
                continue
            device_data = devices.get(id).copy() if id in devices else \
                {'id': id, 'name': id, 'layout': None}

            if id in self.name_aliases:
                device_data['name'] = self.name_aliases[id]

            layout = device_data['layout']

            setattr(self, 'color_layout', self.layout_colors.get(layout))

            if layout in self.layout_aliases:
                device_data['layout'] = self.layout_aliases[layout]

            texts.append(self.py3.safe_format(self.format_device,
                                              device_data))
            if self.top > 0 and len(texts) >= self.top:
                break

        data = {'devices': None}
        if len(texts) > 0:
            if self.display_reverse:
                texts.reverse()

            data['devices'] = \
                self.py3.composite_join(self.format_separator, texts)

        full_text = self.py3.safe_format(self.format, data)

        return {
            'full_text': full_text,
            'cached_until': self.py3.time_in(self.cache_timeout),
        }
