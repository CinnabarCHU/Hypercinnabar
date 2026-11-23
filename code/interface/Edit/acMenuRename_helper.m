function retval = acMenuRename_helper(varargin)
% Edit > Rename (menu_rename). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_rename','helper',varargin{:});
end
