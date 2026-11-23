function retval = acMenuMovGauss_plotter(varargin)
% Timeseries > Smoothing > Moving Gaussian (menu_movGauss). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_movGauss','plotter',varargin{:});
end
