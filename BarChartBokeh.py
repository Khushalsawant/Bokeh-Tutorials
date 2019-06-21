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
from bokeh.core.properties import value

from bokeh.models import ColumnDataSource #,DatetimeTickFormatter
from bokeh.models import HoverTool, WheelZoomTool,ResetTool,SaveTool
from bokeh.transform import dodge


path = "C:/Users/khushal/Documents/Python Scripts/Baji Yakkati Project/Sample_updated.xlsx"
#Line_df = pd.read_excel(path,sheet_name='Line')
Bar_df = pd.read_excel(path,sheet_name='Bar')
print(Bar_df.dtypes)

N=30
x_min = Bar_df['Date'].head(10).min() - pd.Timedelta(days=0.1*N)
x_max = Bar_df['Date'].head(10).max() + pd.Timedelta(days=0.1*N)

Date_list = Bar_df['Date'].tolist()
Process_1 = Bar_df['Process1'].tolist()

output_file('Bar_chart.html',
                title='Bar_chart_for_Processes')

colors = ["#c9d9d3", "#718dbf"]

Process = ["Process_1", "Process_2"]

#source = ColumnDataSource(data=Bar_df)
source_hover = ColumnDataSource(data=dict(Date_list=Bar_df['Date'].head(10).tolist(),
                                              Process_1=Bar_df['Process1'].head(10).tolist(),
                                              Process_2=Bar_df['Process2']. head(10).tolist()
                                              ))


def get_width():
    mindate = min(source_hover.data['Date_list'])
    maxdate = max(source_hover.data['Date_list'])
    return 0.8 * (maxdate-mindate).total_seconds()*1000 / len(source_hover.data['Date_list'])

def get_y_range_values():
    min_value_P1 = min(source_hover.data['Process_1'])
    max_value_P1 = max(source_hover.data['Process_1'])
    min_value_P2 = min(source_hover.data['Process_2'])
    max_value_P2 = max(source_hover.data['Process_2'])
    
    if min_value_P1 > min_value_P2:
        y_min = min_value_P2 - min_value_P2*0.5
    else:
        y_min = min_value_P1 - min_value_P1*0.5

    if max_value_P1 > max_value_P2:
        y_max = max_value_P1 + max_value_P1*0.5
    else:
        y_max = max_value_P2 + max_value_P2*0.5
    return y_max,y_min

max_value,min_value = get_y_range_values()
    
p = figure(plot_width=950, plot_height=600,
           #tools=[hover],
           tools="hover",tooltips="@ $name: @$name",
           x_range=(x_min,x_max),
           y_range=(min_value,max_value),
           #logo=None,
           title="Rec count for Date",x_axis_type="datetime") 

        
p.vbar(x=dodge('Date_list',value=max_value,range=p.x_range),
       top='Process_1',
       source=source_hover,
       color="red",bottom=0, 
       legend=value('Process_1'),
       name="Process_1",
       width=get_width())

p.vbar(x=dodge('Date_list',value=max_value,range=p.x_range),
       top='Process_2',
       source=source_hover,
       color="blue",bottom=0, 
       legend=value('Process_2'),
       name="Process_2",
       width=get_width())

p.add_tools(ResetTool(),SaveTool(),WheelZoomTool())
#p.y_range.range_padding = 0.1
p.xgrid.grid_line_color = None
p.legend.location = "top_right"
p.legend.click_policy = "hide"
p.legend.orientation = "horizontal"
p.toolbar.logo = None
p.sizing_mode = "scale_both"


script0, div0 = components(p)
#print("Script compo=.",script0,"div comp.",div0)

show(p)