# -*- coding: utf-8 -*-
#!/bin/env/python3 

import matplotlib.pyplot

def projection_plot(data_obj, quantity, axis=0, mass_weighted=False, save=False,
                    name="projection_plot", encoding="pdf"):
                    
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
    
    figure, ax = p.subplots()
    
    ax.frame_on(top=False, bottom=False, right=False, left=False)
    
    im = ax.imshow(data, cmap='viridis', interpolation='nearest')
    
    if save:
        p.savefig(name+"."+encoding, bbox_inches='tight')
    p.show()
    
    
    
    
    
        
        