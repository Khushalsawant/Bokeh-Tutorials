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

from bokeh.models import ColumnDataSource , DatetimeTickFormatter
from bokeh.models import FactorRange
from bokeh.models import HoverTool, WheelZoomTool,ResetTool,SaveTool
from bokeh.transform import dodge
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral6
from bokeh.models.widgets import Panel, Tabs
from bokeh.embed import components

path = "C:/Users/KS5046082/Documents/Python Scripts/Sample.xlsx"
#Line_df = pd.read_excel(path,sheet_name='Line')
Bar_df = pd.read_excel(path,sheet_name='Bar')
#print(Bar_df.dtypes)

N=30
x_min = Bar_df['Date'].head(10).min() - pd.Timedelta(days=0.1*N)
x_max = Bar_df['Date'].head(10).max() + pd.Timedelta(days=0.1*N)


Date_list = Bar_df['Date'].head(10).tolist()
Date_list = [d.strftime('%m-%d-%Y') for d in Date_list]
Process_1 = Bar_df['Process1'].head(10).tolist()
Process_2 = Bar_df['Process2'].head(10).tolist()

process_type = ['Process1','Process2']

#########################

data1={'Date_list':Date_list,
      'Process_1':Process_1,
      'Process_2':Process_2}

source1=ColumnDataSource(data=data1)

def get_y_range_values():
    min_value_P1 = min(source1.data['Process_1'])
    max_value_P1 = max(source1.data['Process_1'])
    min_value_P2 = min(source1.data['Process_2'])
    max_value_P2 = max(source1.data['Process_2'])
    
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

hover_value =  HoverTool(tooltips=[
            ("% Process_1", "@Process_1"),
            ("% Process_2", "@Process_2"),
            ])

p = figure(x_range=Date_list, y_range=(min_value,max_value),
           plot_height=350,plot_width=550,
           title="Rec Counts by Date",
           tools=[hover_value])#,tooltips="@ $name: @$name")
           #toolbar_location=None, tools="")

p.vbar(x=dodge('Date_list', -0.25, range=p.x_range), top='Process_1', width=0.2, source=source1,
       color="#c9d9d3", legend=value('Process_1'))

p.vbar(x=dodge('Date_list',  0.0,  range=p.x_range), top='Process_2', width=0.2, source=source1,
       color="#718dbf", legend=value('Process_2'))

p.x_range.range_padding = 0.1
p.xgrid.grid_line_color = None
p.xaxis.major_label_orientation = 1.5
p.add_tools(ResetTool(),SaveTool(),WheelZoomTool())
p.legend.location = "top_right"
p.title_location = "above"
p.toolbar.logo = None
p.legend.orientation = "horizontal"
p.sizing_mode = "scale_both"


tab_10_Days_process = Panel(child=p, title = '10_Days_process')

'''
Graph for Monthly process
'''
Bar_df['Date'] = Bar_df['Date'].dt.strftime('%m/%Y')
Bar_df_grpby = Bar_df.groupby(['Date']).sum()
Bar_df_grpby.reset_index(inplace=True)
print(Bar_df_grpby)
Date_list1 = Bar_df_grpby['Date'].tolist()

#Date_list1 = [d.strftime('%m-%d-%Y') for d in Date_list1]
Process_11 = Bar_df_grpby['Process1'].tolist()
Process_21 = Bar_df_grpby['Process2'].tolist()


process_type = ['Process1','Process2']

#########################

data1={'Date_list':Date_list1,
      'Process_1':Process_11,
      'Process_2':Process_21}
print(data1)
source1=ColumnDataSource(data=data1)

def get_y_range_values():
    min_value_P1 = min(source1.data['Process_1'])
    max_value_P1 = max(source1.data['Process_1'])
    min_value_P2 = min(source1.data['Process_2'])
    max_value_P2 = max(source1.data['Process_2'])
    
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

hover_value =  HoverTool(tooltips=[
            ("% Process_1", "@Process_1"),
            ("% Process_2", "@Process_2"),
            ])

p_all = figure(x_range=Date_list, y_range=(min_value,max_value),
           plot_height=350,plot_width=550,
           title="Rec Counts by Date",
           tools=[hover_value])#,tooltips="@ $name: @$name")
           #toolbar_location=None, tools="")

p_all.vbar(x=dodge('Date_list', -0.25, range=p.x_range), top='Process_1',
           width=0.2, source=source1, color="#c9d9d3", legend=value('Process_1'))

p_all.vbar(x=dodge('Date_list',  0.0,  range=p.x_range), top='Process_2',
           width=0.2, source=source1,color="#718dbf", legend=value('Process_2'))

p_all.x_range.range_padding = 0.1
p_all.xgrid.grid_line_color = None
p_all.xaxis.major_label_orientation = 1.5
p_all.add_tools(ResetTool(),SaveTool(),WheelZoomTool())
p_all.legend.location = "top_right"
p_all.title_location = "above"
p_all.toolbar.logo = None
p_all.legend.orientation = "horizontal"
p_all.sizing_mode = "scale_both"


tab_Overall_process = Panel(child=p_all, title = 'Monthly_process')

tabs = Tabs(tabs=[tab_Overall_process,tab_10_Days_process])
script_line, div_line = components(tabs)
show(tabs)