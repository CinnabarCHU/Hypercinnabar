function retval = acMenuCoh_analyzer(params,varargin)
% Timeseries > Coherence & Phase (menu_coh). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_coh','analyzer',params,varargin{:});
end
