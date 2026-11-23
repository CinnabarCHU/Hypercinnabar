function retval = acMenuMovmedian_analyzer(params,varargin)
% Timeseries > Smoothing > Moving Median > Fixed Count (K-point) (menu_movmedian). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_movmedian','analyzer',params,varargin{:});
end
