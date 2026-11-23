function retval = acMenuDynotV2_analyzer(params,varargin)
% Timeseries > Sedimentary Noise Model > Dynamic noise after orbital tuning (DYNOT) v2 (menu_dynot_v2). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_dynot_v2','analyzer',params,varargin{:});
end
