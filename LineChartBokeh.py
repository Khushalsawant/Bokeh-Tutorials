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
from bokeh.models import ColumnDataSource,DatetimeTickFormatter
from bokeh.models import HoverTool, WheelZoomTool,ResetTool,SaveTool
from bokeh.models.widgets import Panel, Tabs

#path = "C:/Users/khushal/Documents/Python Scripts/Baji Yakkati Project/Sample_upodated.xlsx"
#Line_df = pd.read_excel(path,sheet_name='Line')
#Bar_df = pd.read_excel(path,sheet_name='Bar')

path = "C:/Users/khushal/Documents/Python Scripts/Baji Yakkati Project/sample.json"
Line_df=pd.read_json(path, orient='values')
print(Line_df.columns,Line_df.dtypes)
print(Line_df)
Line_df['odate'] =  pd.to_datetime(Line_df['odate'])
#Line_df['odate'].dt.strftime('%Y-%m-%d')
print(Line_df.dtypes)

'''
odate
SYS1-PYDATA-ALIP-DOMAIN-LOAD
SYS1-PYDATA-AS400-DOMAIN-LOAD
SYS1-PYDATA-OPAS-DOMAIN-LOAD
SYS1-PYDATA-PRODUCER-REP-DOMAIN-LOAD

SYS1_PYDATA_ALIP_DOMAIN_LOAD
SYS1_PYDATA_AS400_DOMAIN_LOAD
SYS1_PYDATA_OPAS_DOMAIN_LOAD
SYS1_PYDATA_PRODUCER_REP_DOMAIN_LOAD
'''
output_file('Line_chart.html',
                title='Line_chart_for_Processes')
N=10
x_min = Line_df['odate'].min() - pd.Timedelta(days=0.1*N)
x_max = Line_df['odate'].max() + pd.Timedelta(days=0.1*N)


''' 
generate a graph for 10-Days records
'''
source_hover_10 = ColumnDataSource(data=dict(odate=Line_df['odate'].head(3).tolist(),
                                              SYS1_PYDATA_ALIP_DOMAIN_LOAD=Line_df['SYS1-PYDATA-ALIP-DOMAIN-LOAD'].head(3).tolist(),
                                              SYS1_PYDATA_AS400_DOMAIN_LOAD=Line_df['SYS1-PYDATA-AS400-DOMAIN-LOAD'].head(3).tolist(),
                                              SYS1_PYDATA_OPAS_DOMAIN_LOAD=Line_df['SYS1-PYDATA-OPAS-DOMAIN-LOAD'].head(3).tolist(),
                                              SYS1_PYDATA_PRODUCER_REP_DOMAIN_LOAD=Line_df['SYS1-PYDATA-PRODUCER-REP-DOMAIN-LOAD'].head(3).tolist()
                                              ))

# show the tooltip
hover_10 = HoverTool(tooltips=[
            ("% SYS1_PYDATA_ALIP_DOMAIN_LOAD", "@SYS1_PYDATA_ALIP_DOMAIN_LOAD"),
            ("% SYS1_PYDATA_AS400_DOMAIN_LOAD", "@SYS1_PYDATA_AS400_DOMAIN_LOAD"),
            (" SYS1_PYDATA_OPAS_DOMAIN_LOAD", "@SYS1_PYDATA_OPAS_DOMAIN_LOAD"),
            (" SYS1_PYDATA_PRODUCER_REP_DOMAIN_LOAD", "@SYS1_PYDATA_PRODUCER_REP_DOMAIN_LOAD"),
            ])
x_min = Line_df['odate'].head(10).min() - pd.Timedelta(days=0.1*N)
x_max = Line_df['odate'].head(10).max() + pd.Timedelta(days=0.1*N)
l_10 = figure(title="Process execution time",
           x_range = (x_min, x_max),
           #logo=None,
           x_axis_type="datetime",tools=[hover_10])
l_10.circle('odate','SYS1_PYDATA_ALIP_DOMAIN_LOAD', size=3, color='red',source=source_hover_10,legend='% SYS1_PYDATA_ALIP_DOMAIN_LOAD')
l_10.line('odate','SYS1_PYDATA_ALIP_DOMAIN_LOAD',source=source_hover_10, legend='% SYS1_PYDATA_ALIP_DOMAIN_LOAD', color='red')

l_10.circle('odate','SYS1_PYDATA_AS400_DOMAIN_LOAD', size=3, color='lavender',source=source_hover_10,legend='% SYS1_PYDATA_AS400_DOMAIN_LOAD')
l_10.line('odate','SYS1_PYDATA_AS400_DOMAIN_LOAD',source=source_hover_10, legend='% SYS1_PYDATA_AS400_DOMAIN_LOAD', color='lavender')

l_10.circle('odate','SYS1_PYDATA_OPAS_DOMAIN_LOAD', size=3, color='lavender',source=source_hover_10,legend='% SYS1_PYDATA_OPAS_DOMAIN_LOAD')
l_10.line('odate','SYS1_PYDATA_OPAS_DOMAIN_LOAD',source=source_hover_10, legend='% SYS1_PYDATA_OPAS_DOMAIN_LOAD', color='blue')

l_10.circle('odate','SYS1_PYDATA_PRODUCER_REP_DOMAIN_LOAD', size=3, color='lavender',source=source_hover_10,legend='% SYS1_PYDATA_PRODUCER_REP_DOMAIN_LOAD')
l_10.line('odate','SYS1_PYDATA_PRODUCER_REP_DOMAIN_LOAD',source=source_hover_10, legend='% SYS1_PYDATA_PRODUCER_REP_DOMAIN_LOAD', color='orange')

l_10.add_tools(ResetTool(),SaveTool(),WheelZoomTool())
l_10.legend.location = "top_right"
l_10.title_location = "above"
l_10.toolbar.logo = None
l_10.legend.click_policy = "hide"
l_10.sizing_mode = "scale_both"
l_10.xaxis.formatter=DatetimeTickFormatter(
                days = ['%m/%d', '%a%d'],
                months = ['%m/%Y', '%b %Y']
                )

tab_Line_Days10 = Panel(child=l_10, title = '10_days process data')
#script0, div0 = components(l)


'''
generate a graph for Monthly records
'''
Line_df['odate'] = Line_df['odate'].dt.strftime('%B/%Y')
Line_df_grpby = Line_df.groupby(['odate']).sum()
Line_df_grpby.reset_index(inplace=True)
print(Line_df_grpby.columns)

source_hover_monthly = ColumnDataSource(data=dict(odate=Line_df_grpby['odate'].tolist(),
                                              SYS1_PYDATA_ALIP_DOMAIN_LOAD=Line_df_grpby['SYS1-PYDATA-ALIP-DOMAIN-LOAD'].tolist(),
                                              SYS1_PYDATA_AS400_DOMAIN_LOAD=Line_df_grpby['SYS1-PYDATA-AS400-DOMAIN-LOAD'].tolist(),
                                              SYS1_PYDATA_OPAS_DOMAIN_LOAD=Line_df_grpby['SYS1-PYDATA-OPAS-DOMAIN-LOAD'].tolist(),
                                              SYS1_PYDATA_PRODUCER_REP_DOMAIN_LOAD=Line_df_grpby['SYS1-PYDATA-PRODUCER-REP-DOMAIN-LOAD'].tolist()
                                              ))
# show the tooltip
hover_monthly = HoverTool(tooltips=[
            ("% SYS1_PYDATA_ALIP_DOMAIN_LOAD", "@SYS1_PYDATA_ALIP_DOMAIN_LOAD"),
            ("% SYS1_PYDATA_AS400_DOMAIN_LOAD", "@SYS1_PYDATA_AS400_DOMAIN_LOAD"),
            ("% SYS1_PYDATA_OPAS_DOMAIN_LOAD", "@SYS1_PYDATA_OPAS_DOMAIN_LOAD"),
            ("% SYS1_PYDATA_PRODUCER_REP_DOMAIN_LOAD", "@SYS1_PYDATA_PRODUCER_REP_DOMAIN_LOAD"),
            ])
#x_min = Line_df_grpby['odate'].min() - pd.Timedelta(days=0.1*N)
#x_max = Line_df_grpby['odate'].max() + pd.Timedelta(days=0.1*N)

l_monthly = figure(title="Process execution time",
           x_range = Line_df_grpby['odate'].tolist(),
           #logo=None,
           #x_axis_type="odatetime",
           tools=[hover_monthly])
l_monthly.circle('odate','SYS1_PYDATA_ALIP_DOMAIN_LOAD', size=3, color='red',source=source_hover_monthly,legend='% SYS1_PYDATA_ALIP_DOMAIN_LOAD')
l_monthly.line('odate','SYS1_PYDATA_ALIP_DOMAIN_LOAD',source=source_hover_monthly, legend='% SYS1_PYDATA_ALIP_DOMAIN_LOAD', color='red')

l_monthly.circle('odate','SYS1_PYDATA_AS400_DOMAIN_LOAD', size=3, color='lavender',source=source_hover_monthly,legend='% SYS1_PYDATA_AS400_DOMAIN_LOAD')
l_monthly.line('odate','SYS1_PYDATA_AS400_DOMAIN_LOAD',source=source_hover_monthly, legend='% SYS1_PYDATA_AS400_DOMAIN_LOAD', color='lavender')

l_monthly.circle('odate','SYS1_PYDATA_OPAS_DOMAIN_LOAD', size=3, color='lavender',source=source_hover_monthly,legend='% SYS1_PYDATA_OPAS_DOMAIN_LOAD')
l_monthly.line('odate','SYS1_PYDATA_OPAS_DOMAIN_LOAD',source=source_hover_monthly, legend='% SYS1_PYDATA_OPAS_DOMAIN_LOAD', color='blue')

l_monthly.circle('odate','SYS1_PYDATA_PRODUCER_REP_DOMAIN_LOAD', size=3, color='lavender',source=source_hover_monthly,legend='% SYS1_PYDATA_PRODUCER_REP_DOMAIN_LOAD')
l_monthly.line('odate','SYS1_PYDATA_PRODUCER_REP_DOMAIN_LOAD',source=source_hover_monthly, legend='% SYS1_PYDATA_PRODUCER_REP_DOMAIN_LOAD', color='orange')

l_monthly.add_tools(ResetTool(),SaveTool(),WheelZoomTool())
l_monthly.legend.location = "top_right"
l_monthly.title_location = "above"
l_monthly.toolbar.logo = None
l_monthly.legend.click_policy = "hide"
l_monthly.sizing_mode = "scale_both"

l_monthly.xaxis.formatter=DatetimeTickFormatter(
                days = ['%B/%d', '%a%d'],
                )

tab_Line_Days_monthly = Panel(child=l_monthly, title = 'Monthly process data')

tabs = Tabs(tabs=[tab_Line_Days10,tab_Line_Days_monthly])
script_line, div_line = components(tabs)
show(tabs)
#print(script_line, div_line)
