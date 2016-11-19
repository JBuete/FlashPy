# -*- coding: utf-8 -*-
#!/bin/env/python3 

import matplotlib.pyplot
import numpy

def projection_plot(data_obj, quantity, axis=0, mass_weighted=False, save=False,
                    name="projection_plot", encoding="pdf", cmap='viridis',
                    colorbar_on=True, colorbar_side='left'):
                    
    # recover the data set that we want to get 
    data = data_obj.get_values(quantity, unpack=True)
    
    if mass_weighted:
        # if we are mass weighting then we need to get the densities out
        masses = data_obj.get_values('dens', unpack=True)
        
        # scale the data by the densities
        data *= masses
        
        data = data.sum(axis=axis)
        masses = masses.sum(axis=axis)
        
        data /= masses
    else:
        data = data.sum(axis=axis)
    
    
    # now organise the plot
    figure, ax = matplotlib.pyplot.subplots(frameon=False)
    
    
    # turn off the ticks and the labels because we only want to see the image
    ax.tick_params(top=False, bottom=False, right=False, left=False, 
                    labelbottom=False, labelleft=False)
    
    
    # show the image nearest interpolation is used as this removes most of the 
    # actual interpolation and works with all encodings of the image
    im = ax.imshow(data, cmap=cmap, interpolation='nearest', vmax=numpy.max(data),
                    vmin=numpy.min(data))
    
    # add the colorbar if wanted 
    if colorbar_on:
        # put the colorbar on the side of the image
        cbaxes = figure.add_axes([0.15, 0.13, 0.03, 0.75])
        cbaxes.yaxis.set_ticks_position(colorbar_side)
        
        # figure out the positions of the ticks on the colorbar
        positions = [float("{:.4f}".format(pos)) for pos in 
                numpy.linspace(numpy.min(data), numpy.max(data), 5).tolist()]
        
        
        cb = figure.colorbar(im, label="", cax=cbaxes, ticks=positions)
        cb.set_label(r"", size=15)
        cb.set_ticklabels(positions)
        cb.ax.yaxis.set_ticks_position(colorbar_side)
        cb.ax.yaxis.set_label_position(colorbar_side)
    
    
    if save:
        matplotlib.pyplot.savefig(name+"."+encoding, bbox_inches='tight')
    matplotlib.pyplot.show()
    
    

    
    
        
        