function retval = acMenuWhiten_plotter(varargin)
% Timeseries > Pre-whitening (menu_whiten). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_whiten','plotter',varargin{:});
end
