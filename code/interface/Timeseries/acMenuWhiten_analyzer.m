function retval = acMenuWhiten_analyzer(params,varargin)
% Timeseries > Pre-whitening (menu_whiten). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_whiten','analyzer',params,varargin{:});
end
