function retval = acMenuPrewhiten_plotter(varargin)
% Timeseries > Detrending | Curve Fitting (menu_prewhiten). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_prewhiten','plotter',varargin{:});
end
