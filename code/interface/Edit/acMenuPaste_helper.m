function retval = acMenuPaste_helper(varargin)
% Edit > Paste (menu_paste). See acMenuCatalog for available operations.
retval = acMenuInvoke('menu_paste','helper',varargin{:});
end
