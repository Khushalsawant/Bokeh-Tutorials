import logging
from random import randint
from bokeh.plotting import figure, show,output_file
from bokeh.models import HoverTool, NumeralTickFormatter,SaveTool
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

""" (W/m2K4) - The Stefan-Boltzmann Constant"""
sb_constant = 5.6703 * pow(10,-8)

"""
q = sb_constant* Temp * ar
where
q = heat transfer per unit time (W)
sb_constant = 5.6703 10-8 (W/m2K4) - The Stefan-Boltzmann Constant
Temp = temperature
ar = area of the emitting body (m2)
"""
LOG = logging.getLogger('radiation_equation')

def calculate_heat_trasnfer(constant_field='Temperature',):
    LOG.debug('calculate_heat_trasnfer')
    #area_list = [randint(9**(9-i), (9**9)-i) for i in range(0,10)]
    area_list = [ (10**5)*i for i in range(1,11)]
    if constant_field == 'Temperature':
        hf = []
        #Temp = 6000 # Temp of Sun in kelvin
        Temp = 288 # Temp of Earth in kelvin
        for ar_m2 in area_list:
            q = sb_constant* Temp * ar_m2
            hf.append(q)
        hf_data = dict(zip(area_list,hf))
        LOG.debug('graphical_data_plotting')
        x = list(hf_data.keys())
        y = list(hf_data.values())

        LOG.info('values for x axis= {0}'.format(x))
        LOG.info('values for y axis= {0}'.format(y))

        hover_10 = HoverTool(tooltips=[
            ("Heat Transfer per Unit time","@y{0[.]00}"),
            ("Area in M2","@x{0[.]0000000000}")
        ],
            # display a tooltip whenever the cursor is vertically in line with a glyph
            mode='mouse'
        )
        # set output to static HTML file
        output_file(filename="Area_vs_Heat_Transfer.html", title="Area_vs_Heat_Transfer")

        # create a new plot with a title and axis labels
        p = figure(title="Heat Transfer Graphical example",
                   y_axis_label="Heat Transfer per Unit time",
                   x_axis_label="Area in M2",
                   #sizing_mode="scale_width",
                   tools=[hover_10,SaveTool()])

        # add a line renderer with legend and line thickness
        line = p.line(x, y, legend_label="Area vs Heat Transfer", line_width=2)
        circle = p.circle(
            x,
            y,
            legend_label="Area vs Heat Transfer",
            fill_color="red",
            fill_alpha=0.5,
            line_color="blue",
            size=5,
        )
        # display legend in top left corner (default is top right corner)
        p.xaxis[0].formatter = NumeralTickFormatter(format="0[.]0000000000")
        p.legend.location = "top_left"
        p.toolbar.logo = None
        p.toolbar.active_drag = None
        p.legend.click_policy = "hide"
        # add a title to your legend
        p.legend.title = "Obervations"
        # show the results
        show(p)
    elif constant_field=='heat_transfer':
        hf = []
        q=15
        for ar_m2 in area_list:
            Temp = q/(sb_constant* ar_m2)
            hf.append(Temp)
        hf_data = dict(zip(area_list,hf))
        LOG.debug('graphical_data_plotting')
        x = list(hf_data.keys())
        y = list(hf_data.values())

        LOG.info('values for x axis= {0}'.format(x))
        LOG.info('values for y axis= {0}'.format(y))

        hover_10 = HoverTool(tooltips=[
            ("Temperature","@y{0[.]00}"),
            ("Area in M2","@x{0[.]0000000000}")
        ],
            # display a tooltip whenever the cursor is vertically in line with a glyph
            mode='mouse'
        )
        output_file(filename="Area_vs_Temperature.html", title="Area_vs_Temperature")
        # create a new plot with a title and axis labels
        p = figure(title="Heat Transfer Graphical example",
                   y_axis_label="Temperature",
                   x_axis_label="Area in M2",
                   #sizing_mode="scale_width",
                   tools=[hover_10,SaveTool()])

        # add a line renderer with legend and line thickness
        line = p.line(x, y, legend_label="Area vs Temperature", line_width=2)
        circle = p.circle(
            x,
            y,
            legend_label="Area vs Temperature",
            fill_color="red",
            fill_alpha=0.5,
            line_color="blue",
            size=5,
        )
        # display legend in top left corner (default is top right corner)
        p.legend.location = "top_left"
        p.toolbar.logo = None
        p.toolbar.active_drag = None
        p.legend.click_policy = "hide"
        p.xaxis[0].formatter = NumeralTickFormatter(format="0[.]0000000000")
        # add a title to your legend
        p.legend.title = "Obervations"

        # show the results
        show(p)
    else:
        LOG.info('Invalid Constant field is entered, value is {0}'.format(constant_field))

def calculate_heat_trasnfer_maptplotlb(constant_field='Temperature'):
    LOG.debug('calculate_heat_trasnfer')
    #area_list = [randint(9**(9-i), (9**9)-i) for i in range(0,10)]
    area_list = [ (10**5)*i for i in range(1,11)]
    if constant_field == 'Temperature':
        hf = []
        #Temp = 6000 # Temp of Sun in kelvin
        Temp = 288 # Temp of Earth in kelvin
        for ar_m2 in area_list:
            q = sb_constant* Temp * ar_m2
            hf.append(q)
        hf_data = dict(zip(area_list,hf))
        LOG.debug('graphical_data_plotting')
        x = list(hf_data.keys())
        y = list(hf_data.values())
        LOG.info('values for x axis= {0}'.format(x))
        LOG.info('values for y axis= {0}'.format(y))
        fig, ax = plt.subplots()
        ax.plot(x, y,label='Area vs Heat Transfer')
        ax.scatter(x, y,label='Area vs Heat Transfer')
        ax.set_xlabel("Area in M2")  # add X-axis label
        ax.set_ylabel("Heat Transfer per Unit time")  # add Y-axis label
        ax.set_title("Area vs Heat Transfer")  # add title
        ax.xaxis.set_major_formatter(FormatStrFormatter('% 1.2f'))
        #ax.yaxis.set_major_formatter(FormatStrFormatter('% 1.2f'))
        ax.grid(True)
        for i in range(len(y)):
            #ax.text(x[i], y[i]+y[i]/10, "y={0}".format(round(y[i],2)), ha="center")
            ax.text(x[i], y[i]+y[0]/10, "%1.2f" %y[i], ha="center")
        plt.savefig("Area vs Heat Transfer.png")
        plt.show()
    elif constant_field=='heat_transfer':
        hf = []
        q=15
        for ar_m2 in area_list:
            Temp = q/(sb_constant* ar_m2)
            hf.append(Temp)
        hf_data = dict(zip(area_list,hf))
        LOG.debug('graphical_data_plotting')
        x = list(hf_data.keys())
        y = list(hf_data.values())

        LOG.info('values for x axis= {0}'.format(x))
        LOG.info('values for y axis= {0}'.format(y))
        fig, ax = plt.subplots()
        ax.plot(x, y,label='Area vs Heat Transfer')
        ax.scatter(x, y,label='Area vs Heat Transfer')
        ax.set_xlabel("Area in M2")  # add X-axis label
        ax.set_ylabel("Temperature")  # add Y-axis label
        ax.set_title("Area vs Temperature ")  # add title
        ax.xaxis.set_major_formatter(FormatStrFormatter('% 1.2f'))
        #ax.yaxis.set_major_formatter(FormatStrFormatter('% 1.2f'))
        ax.grid(True)
        for i in range(len(y)):
            #ax.text(x[i], y[i]+y[i]/10, "y={0}".format(round(y[i],2)), ha="center")
            ax.text(x[i], y[i]+y[0]/100, "%1.2f" %y[i], ha="center")
        plt.savefig("Area vs Temperature.png")
        plt.show()

if __name__ == '__main__':
    pass
    #calculate_heat_trasnfer('heat_transfer')
    #calculate_heat_trasnfer_maptplotlb(constant_field='Temperature')
    #calculate_heat_trasnfer_maptplotlb(constant_field='heat_transfer')
    #calculate_heat_trasnfer('Temperature')
