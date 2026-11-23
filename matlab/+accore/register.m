function [menu,engine] = register(tag,operation)
% Discover menu contracts and select the historical default or a pinned implementation.
catalog = acMenuCatalog();
if nargin == 0
    for k = 1:numel(catalog.menus)
        catalog.menus(k).default = preferred(catalog.menus(k));
    end
    menu = catalog;
    return
end
menu = acMenuCatalog(char(tag));
menu.default = preferred(menu);
if nargout < 2 && nargin < 2, return; end
if nargin < 2 || isempty(operation), operation = menu.default; end
if isempty(operation), error('Acycle:Core:Heading','%s is a menu heading.',menu.tag); end
engine = acMenuEngine(menu,char(operation));
end

function operation = preferred(menu)
operation = menu.default;
legacy = [operation,'_legacy'];
if ~isempty(menu.guide) && ismember(legacy,strsplit(menu.choices))
    operation = legacy;
elseif strcmp(menu.tag,'menu_leadlag')
    operation = 'rmse4leadlag_legacy';
elseif strcmp(menu.tag,'menu_specmoments')
    operation = 'spectralmoments_legacy';
end
end
