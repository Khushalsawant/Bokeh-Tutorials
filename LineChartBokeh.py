# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 12:19:52 2019

@author: KS5046082
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
''' 
Packages for embedding graph on webpage
'''
from bokeh.embed import components
from bokeh.plotting import figure, output_file ,show
from bokeh.models import ColumnDataSource,DatetimeTickFormatter,LabelSet
from bokeh.models import HoverTool, WheelZoomTool,ResetTool,SaveTool
from bokeh.models.widgets import Panel, Tabs

path = "C:/Users/khushal/Documents/Python Scripts/Baji Yakkati Project/Sample_updated.xlsx"
Line_df = pd.read_excel(path,sheet_name='Line')
#Bar_df = pd.read_excel(path,sheet_name='Bar')

output_file('Line_chart.html',
                title='Line_chart_for_Processes')
N=30
x_min = Line_df['Date'].min() - pd.Timedelta(days=0.1*N)
x_max = Line_df['Date'].max() + pd.Timedelta(days=0.1*N)

print(Line_df.columns,Line_df.dtypes)

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
l.toolbar.logo = None
l.legend.click_policy = "hide"
l.sizing_mode = "scale_both"
l.xaxis.formatter=DatetimeTickFormatter(
                days = ['%m/%d', '%a%d'],
                )

#script0, div0 = components(l)
#print("Script compo=.",script0,"div comp.",div0)

#show(l)

# Make a tab with the layout 
tab_overall_process = Panel(child=l, title = 'Overall process')

'''
generate a graph for 10-Days records
'''
source_hover_10 = ColumnDataSource(data=dict(Date=Line_df['Date'].head(10).tolist(),
                                              Process_1=Line_df['Process1'].head(10).tolist(),
                                              Process_2=Line_df['Process2'].head(10).tolist(),
                                              Process_3=Line_df['Process3'].head(10).tolist(),
                                              Process_4=Line_df['Process4'].head(10).tolist()
                                              ))

# show the tooltip
hover_10 = HoverTool(tooltips=[
            ("% Process_1", "@Process_1"),
            ("% Process_2", "@Process_2"),
            ("% Process_3", "@Process_3"),
            ("% Process_4", "@Process_4"),
            ])
x_min = Line_df['Date'].head(10).min() - pd.Timedelta(days=0.1*N)
x_max = Line_df['Date'].head(10).max() + pd.Timedelta(days=0.1*N)
l_10 = figure(title="Process execution time",
           x_range = (x_min, x_max),
           #logo=None,
           x_axis_type="datetime",tools=[hover_10])
l_10.circle('Date','Process_1', size=3, color='red',source=source_hover_10,legend='% Process_1')
l_10.line('Date','Process_1',source=source_hover_10, legend='% Process_1', color='red')

l_10.circle('Date','Process_2', size=3, color='lavender',source=source_hover_10,legend='% Process_2')
l_10.line('Date','Process_2',source=source_hover_10, legend='% Process_2', color='lavender')

l_10.circle('Date','Process_3', size=3, color='lavender',source=source_hover_10,legend='% Process_3')
l_10.line('Date','Process_3',source=source_hover_10, legend='% Process_3', color='blue')

l_10.circle('Date','Process_4', size=3, color='lavender',source=source_hover_10,legend='% Process_4')
l_10.line('Date','Process_4',source=source_hover_10, legend='% Process_4', color='orange')

l_10.add_tools(ResetTool(),SaveTool(),WheelZoomTool())
l_10.legend.location = "top_right"
l_10.title_location = "above"
l_10.toolbar.logo = None
l_10.legend.click_policy = "hide"
l_10.sizing_mode = "scale_both"
l_10.xaxis.formatter=DatetimeTickFormatter(
                days = ['%m/%d', '%a%d'],
                )

tab_Line_Days10 = Panel(child=l_10, title = '10_days process data')
#script0, div0 = components(l)


'''
generate a graph for Monthly records
'''
Line_df['Date'] = Line_df['Date'].dt.strftime('%B/%Y')
Line_df_grpby = Line_df.groupby(['Date']).sum()
Line_df_grpby.reset_index(inplace=True)
#print(Line_df_grpby.columns)

source_hover_monthly = ColumnDataSource(data=dict(Date=Line_df_grpby['Date'].tolist(),
                                              Process_1=Line_df_grpby['Process1'].tolist(),
                                              Process_2=Line_df_grpby['Process2'].tolist(),
                                              Process_3=Line_df_grpby['Process3'].tolist(),
                                              Process_4=Line_df_grpby['Process4'].tolist()
                                              ))
# show the tooltip
hover_monthly = HoverTool(tooltips=[
            ("% Process_1", "@Process_1"),
            ("% Process_2", "@Process_2"),
            ("% Process_3", "@Process_3"),
            ("% Process_4", "@Process_4"),
            ])
#x_min = Line_df_grpby['Date'].min() - pd.Timedelta(days=0.1*N)
#x_max = Line_df_grpby['Date'].max() + pd.Timedelta(days=0.1*N)

l_monthly = figure(title="Process execution time",
           x_range = Line_df_grpby['Date'].tolist(),
           #logo=None,
           #x_axis_type="datetime",
           tools=[hover_monthly])
l_monthly.circle('Date','Process_1', size=3, color='red',source=source_hover_monthly,legend='% Process_1')
l_monthly.line('Date','Process_1',source=source_hover_monthly, legend='% Process_1', color='red')

l_monthly.circle('Date','Process_2', size=3, color='lavender',source=source_hover_monthly,legend='% Process_2')
l_monthly.line('Date','Process_2',source=source_hover_monthly, legend='% Process_2', color='lavender')

l_monthly.circle('Date','Process_3', size=3, color='lavender',source=source_hover_monthly,legend='% Process_3')
l_monthly.line('Date','Process_3',source=source_hover_monthly, legend='% Process_3', color='blue')

l_monthly.circle('Date','Process_4', size=3, color='lavender',source=source_hover_monthly,legend='% Process_4')
l_monthly.line('Date','Process_4',source=source_hover_monthly, legend='% Process_4', color='orange')

l_monthly.add_tools(ResetTool(),SaveTool(),WheelZoomTool())
l_monthly.legend.location = "top_right"
l_monthly.title_location = "above"
l_monthly.toolbar.logo = None
l_monthly.legend.click_policy = "hide"
l_monthly.sizing_mode = "scale_both"
'''
l_monthly.xaxis.formatter=DatetimeTickFormatter(
                days = ['%B/%d', '%a%d'],
                )
'''
tab_Line_Days_monthly = Panel(child=l_monthly, title = 'Monthly process data')

tabs = Tabs(tabs=[tab_Line_Days10,tab_Line_Days_monthly,tab_overall_process])
script_line, div_line = components(tabs)
show(tabs)
#print(script_line, div_line)
