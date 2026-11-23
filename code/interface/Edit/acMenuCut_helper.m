function retval = acMenuCut_helper(varargin)
% Edit > Cut (menu_cut). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_cut','helper',varargin{:});
end
