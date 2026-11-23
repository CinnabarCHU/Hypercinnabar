function retval = acMenuDelete_helper(varargin)
% Edit > Delete (menu_delete). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_delete','helper',varargin{:});
end
