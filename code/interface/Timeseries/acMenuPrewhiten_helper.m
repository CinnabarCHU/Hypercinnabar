function retval = acMenuPrewhiten_helper(varargin)
% Timeseries > Detrending | Curve Fitting (menu_prewhiten). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_prewhiten','helper',varargin{:});
end
