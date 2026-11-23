function retval = acMenuSmooth_plotter(varargin)
% Timeseries > Smoothing > Moving Average > Fixed Count (K-point) (menu_smooth). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_smooth','plotter',varargin{:});
end
