function retval = acMenuBootstrap_analyzer(params,varargin)
% Timeseries > Smoothing > Bootstrap (menu_bootstrap). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_bootstrap','analyzer',params,varargin{:});
end
