function retval = acMenuPrewhiten_analyzer(params,varargin)
% Timeseries > Detrending | Curve Fitting (menu_prewhiten). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_prewhiten','analyzer',params,varargin{:});
end
