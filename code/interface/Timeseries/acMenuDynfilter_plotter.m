function retval = acMenuDynfilter_plotter(varargin)
% Timeseries > Dynamic Filtering (menu_dynfilter). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_dynfilter','plotter',varargin{:});
end
