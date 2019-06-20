# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 12:19:52 2019

@author: KS5046082
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import timedelta
from datetime import datetime
import os
import numpy as np
''' 
Packages for embedding graph on webpage
'''
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.plotting import figure, output_file ,show
import random
import pandas as pd
from bokeh.models import ColumnDataSource,DatetimeTickFormatter
from bokeh.models import HoverTool, WheelZoomTool,ResetTool,SaveTool

path = "C:/Users/khushal/Documents/Python Scripts/Baji Yakkati Project/Sample_updated.xlsx"
Line_df = pd.read_excel(path,sheet_name='Line')
#Bar_df = pd.read_excel(path,sheet_name='Bar')

output_file('Line_chart.html',
                title='Line_chart_for_Processes')
N=30
x_min = Line_df['Date'].min() - pd.Timedelta(days=0.1*N)
x_max = Line_df['Date'].max() + pd.Timedelta(days=0.1*N)

print(Line_df.columns,Line_df.dtypes)
source = ColumnDataSource(data=Line_df)
source_hover = ColumnDataSource(data=dict(Date=Line_df['Date'].tolist(),
                                              Process_1=Line_df['Process1'].tolist(),
                                              Process_2=Line_df['Process2'].tolist(),
                                              Process_3=Line_df['Process3'].tolist(),
                                              Process_4=Line_df['Process4'].tolist()
                                              ))

# show the tooltip
hover = HoverTool(tooltips=[
            ("% Process_1", "@Process_1"),
            ("% Process_2", "@Process_2"),
            ("% Process_3", "@Process_3"),
            ("% Process_4", "@Process_4"),
            ])

l = figure(title="Process execution time",
           x_range = (x_min, x_max),
           #logo=None,
           x_axis_type="datetime",tools=[hover])
l.circle('Date','Process_1', size=3, color='red',source=source_hover,legend='% Process_1')
glyph_1 = l.line('Date','Process_1',source=source_hover, legend='% Process_1', color='red')

l.circle('Date','Process_2', size=3, color='lavender',source=source_hover,legend='% Process_2')
glyph_2 = l.line('Date','Process_2',source=source_hover, legend='% Process_2', color='lavender')

l.circle('Date','Process_3', size=3, color='lavender',source=source_hover,legend='% Process_3')
glyph_3 = l.line('Date','Process_3',source=source_hover, legend='% Process_3', color='blue')

l.circle('Date','Process_4', size=3, color='lavender',source=source_hover,legend='% Process_4')
glyph_3 = l.line('Date','Process_4',source=source_hover, legend='% Process_4', color='orange')

l.add_tools(ResetTool(),SaveTool(),WheelZoomTool())
l.legend.location = "top_right"
l.title_location = "above"
l.legend.click_policy = "hide"
l.sizing_mode = "scale_both"

l.xaxis.formatter=DatetimeTickFormatter(
                days = ['%m/%d', '%a%d'],
                )

script0, div0 = components(l)
print("Script compo=.",script0,"div comp.",div0)

show(l)