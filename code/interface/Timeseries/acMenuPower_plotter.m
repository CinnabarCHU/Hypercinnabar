function retval = acMenuPower_plotter(varargin)
% Timeseries > Spectral Analysis (menu_power). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_power','plotter',varargin{:});
end
