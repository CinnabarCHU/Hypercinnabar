function retval = acMenuSpecmoments_analyzer(params,varargin)
% Timeseries > Spectral Moments (menu_specmoments). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_specmoments','analyzer',params,varargin{:});
end
