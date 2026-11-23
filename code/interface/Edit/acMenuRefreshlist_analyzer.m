function retval = acMenuRefreshlist_analyzer(params,varargin)
% Edit > Refresh (menu_refreshlist). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_refreshlist','analyzer',params,varargin{:});
end
