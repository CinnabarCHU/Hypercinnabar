function retval = acMenuOpendir_helper(varargin)
% File > Open Directory (menu_opendir). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_opendir','helper',varargin{:});
end
