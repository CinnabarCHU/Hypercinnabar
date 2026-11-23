function retval = acMenuRho_plotter(varargin)
% Timeseries > Sedimentary Noise Model > Lag-1 autocorrelation coefficient (\rho1) (menu_rho). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_rho','plotter',varargin{:});
end
