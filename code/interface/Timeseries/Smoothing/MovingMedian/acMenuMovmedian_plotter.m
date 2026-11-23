function retval = acMenuMovmedian_plotter(varargin)
% Timeseries > Smoothing > Moving Median > Fixed Count (K-point) (menu_movmedian). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_movmedian','plotter',varargin{:});
end
