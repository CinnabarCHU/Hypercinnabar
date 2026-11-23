function retval = acMenuMovmedian_helper(varargin)
% Timeseries > Smoothing > Moving Median > Fixed Count (K-point) (menu_movmedian). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_movmedian','helper',varargin{:});
end
