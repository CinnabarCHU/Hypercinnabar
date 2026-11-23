function engine = acMenuEngine(menu,selector)
if ~(ischar(selector) && isrow(selector) || isstring(selector) && isscalar(selector))
    error('Acycle:Menu:Operation','params.operation must be a registered selector.');
end
selector = char(selector);
if ~ismember(selector,strsplit(menu.choices))
    error('Acycle:Menu:Operation','%s has no operation "%s". See acMenuCatalog.',menu.tag,selector);
end
catalog = acMenuCatalog();
engine = catalog.engines(strcmp({catalog.engines.operation},selector));
end
