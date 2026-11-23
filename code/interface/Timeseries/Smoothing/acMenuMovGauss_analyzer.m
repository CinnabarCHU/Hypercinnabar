function retval = acMenuMovGauss_analyzer(params,varargin)
% Timeseries > Smoothing > Moving Gaussian (menu_movGauss). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_movGauss','analyzer',params,varargin{:});
end
