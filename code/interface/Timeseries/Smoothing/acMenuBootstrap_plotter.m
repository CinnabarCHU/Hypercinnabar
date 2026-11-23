function retval = acMenuBootstrap_plotter(varargin)
% Timeseries > Smoothing > Bootstrap (menu_bootstrap). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_bootstrap','plotter',varargin{:});
end
