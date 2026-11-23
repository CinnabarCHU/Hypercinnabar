function retval = acMenuWhiten_helper(varargin)
% Timeseries > Pre-whitening (menu_whiten). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_whiten','helper',varargin{:});
end
