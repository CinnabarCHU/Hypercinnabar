function retval = acMenuSmooth_helper(varargin)
% Timeseries > Smoothing > Moving Average > Fixed Count (K-point) (menu_smooth). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_smooth','helper',varargin{:});
end
