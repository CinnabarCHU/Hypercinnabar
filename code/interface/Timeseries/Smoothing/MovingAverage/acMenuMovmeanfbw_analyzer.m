function retval = acMenuMovmeanfbw_analyzer(params,varargin)
% Timeseries > Smoothing > Moving Average > Fixed Bandwidth (menu_movmeanfbw). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_movmeanfbw','analyzer',params,varargin{:});
end
