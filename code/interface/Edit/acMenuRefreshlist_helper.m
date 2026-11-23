function retval = acMenuRefreshlist_helper(varargin)
% Edit > Refresh (menu_refreshlist). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_refreshlist','helper',varargin{:});
end
