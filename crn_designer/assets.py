# -*- coding: utf-8 -*-
"""Application assets."""
from flask_assets import Bundle, Environment

css = Bundle(
    'libs/bootstrap/dist/css/bootstrap.css',
    'css/style.css',
    filters='cssmin',
    output='public/css/common.css'
)

css_spec = Bundle(
    'TimeRails/TimeRails/css/spec.css',
    'crn-sketch-editor/crn-editor.css',
    filters='cssmin',
    output='public/css/spec_css.css'
)

js = Bundle(
    'libs/jQuery/dist/jquery.js',
    'libs/bootstrap/dist/js/bootstrap.js',
    'js/plugins.js',
    filters='jsmin',
    output='public/js/common.js'
)

js_spec = Bundle(
    'libs/d3.v3.4.11.js',
    'libs/d3-context-menu.js',
    'libs/https_cdn.mathjax.org_mathjax_latest_MathJax.js?config=TeX-AMS-MML_HTMLorMML.js',
    'TimeRails/TimeRails/js/spec.js',
    'TimeRails/TimeRails/js/rectangle.js',
    'TimeRails/TimeRails/js/mode.js',
    'TimeRails/TimeRails/js/input.js',
    'TimeRails/TimeRails/js/time_rail.js',
    'TimeRails/TimeRails/js/description.js',
    'crn-sketch-editor/libs/cola.v3.min.js',
    'crn-sketch-editor/crn-editor.js',
    filters='jsmin',
    output='public/js/spec_js.js'
)

assets = Environment()

assets.register('js_all', js)
assets.register('js_spec', js_spec)

assets.register('css_all', css)
assets.register('css_spec', css_spec)
