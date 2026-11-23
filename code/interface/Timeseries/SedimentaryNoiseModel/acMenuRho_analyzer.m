function retval = acMenuRho_analyzer(params,varargin)
% Timeseries > Sedimentary Noise Model > Lag-1 autocorrelation coefficient (\rho1) (menu_rho). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_rho','analyzer',params,varargin{:});
end
