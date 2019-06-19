# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 13:32:59 2019

@author: KS5046082
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import timedelta
from datetime import datetime
import os
import numpy as np
import random
import pandas as pd
''' 
Packages for embedding graph on webpage
'''
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.plotting import figure, output_file ,show

from bokeh.models import ColumnDataSource,DatetimeTickFormatter
from bokeh.models import HoverTool, WheelZoomTool,ResetTool,SaveTool
from bokeh.transform import dodge


path = "C:/Users/khushal/Documents/Python Scripts/Baji Yakkati Project/Sample_updated.xlsx"
#Line_df = pd.read_excel(path,sheet_name='Line')
Bar_df = pd.read_excel(path,sheet_name='Bar')
print(Bar_df.dtypes)
Date_list = Bar_df['Date'].tolist()
print("Date",Date_list)
Process_1 = Bar_df['Process1'].tolist()
print("Process1",Process_1)

output_file('Bar_chart.html',
                title='Bar_chart_for_Processes')

colors = ["#c9d9d3", "#718dbf"]

#source = ColumnDataSource(data=Bar_df)
source_hover = ColumnDataSource(data=dict(Date_list=Bar_df['Date'].head(15).tolist(),
                                              Process_1=Bar_df['Process1'].head(15).tolist(),
                                              Process_2=Bar_df['Process2']. head(15).tolist()
                                              ))

# show the tooltip
hover = HoverTool(tooltips=[("Process_1", "@Process_1"),
                            ("Process_2", "@Process_2")
])
p = figure(plot_width=950, plot_height=600,tools=[hover],
           #y_range=(0,Bar_df['Process1'].max()),
           #logo=None,
           title="Rec count for Date",x_axis_type="datetime") 

p.vbar(x=dodge('Date_list',0.25,p.x_range),
       top='Process_1',
       source=source_hover,
       color="red",bottom=0, 
       width=9999999)

p.vbar(x=dodge('Date_list',0.0,p.x_range),
       top='Process_2',
       source=source_hover,
       color="blue",bottom=0, 
       width=9999999)

'''
p = figure(x_range=Date, y_range=(500, 20000), plot_height=250, title="Fruit Counts by Year",
           toolbar_location=None, tools="")

p.vbar(x=dodge('Date', -0.25, range=p.x_range), top='2015', width=0.2, source=source,
       color="#c9d9d3")#, legend=value("2015"))
'''

p.add_tools(ResetTool(),SaveTool(),WheelZoomTool())
#p.y_range.range_padding = 0.1
p.xgrid.grid_line_color = None
p.legend.location = "top_left"
p.legend.orientation = "horizontal"

show(p)