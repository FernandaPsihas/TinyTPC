import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pedestal_plots
  
def main(filename):

    fig1 = pedestal_plots.plot_xy_and_key(filename)
    fig2 = pedestal_plots.plot_adc_trigger(filename)
    fig3 = pedestal_plots.plot_adc_time(filename)
  
  
    def save_image(filename):
        p = PdfPages(filename)
          
        fig_nums = plt.get_fignums()  
        figs = [plt.figure(n) for n in fig_nums]
        for fig in figs: 
            fig.savefig(p, format='pdf') 
        p.close()  
    
    filename = "multi_pedestal_plots.pdf"  
    save_image(filename)  
