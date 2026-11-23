function item = acMenuCatalog(tag)
% Inspect the pinned menu hierarchy, available selectors and role input contracts.
persistent catalog
if isempty(catalog)
    catalog = jsondecode(fileread(fullfile(fileparts(mfilename('fullpath')),'catalogue.json')));
end
if nargin == 0
    item = catalog;
    return
end
index = find(strcmp({catalog.menus.tag},tag),1);
if isempty(index), error('Acycle:Menu:UnknownMenu','Unknown menu tag %s.',tag); end
item = catalog.menus(index);
end
