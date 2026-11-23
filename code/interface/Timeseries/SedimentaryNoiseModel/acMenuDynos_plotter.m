function retval = acMenuDynos_plotter(varargin)
% Timeseries > Sedimentary Noise Model > Dynamic noise after orbital tuning (DYNOT) (menu_dynos). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_dynos','plotter',varargin{:});
end
