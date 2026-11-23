function retval = acMenuSpecmoments_plotter(varargin)
% Timeseries > Spectral Moments (menu_specmoments). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_specmoments','plotter',varargin{:});
end
