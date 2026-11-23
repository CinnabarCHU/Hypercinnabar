function retval = acMenuSmooth_analyzer(params,varargin)
% Timeseries > Smoothing > Moving Average > Fixed Count (K-point) (menu_smooth). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_smooth','analyzer',params,varargin{:});
end
