function retval = acMenuLyapunov_analyzer(params,varargin)
% Timeseries > Sedimentary Noise Model > Lyapunov exponent (menu_lyapunov). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_lyapunov','analyzer',params,varargin{:});
end
