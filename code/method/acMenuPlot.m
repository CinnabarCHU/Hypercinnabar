function [value,status] = acMenuPlot(menu,engine,s,journal,live)
% Adapt the historical plotter input and preserve its return value and completion status.
if ~ismember('plotter',strsplit(engine.roles))
    error('Acycle:Menu:Role','%s has no plotter in this snapshot.',engine.operation);
end
if ~isempty(s.target) && (~isstruct(s.target) || ~isfield(s.target,'kind') || ...
        ~ismember(s.target.kind,{'axes','figure'}))
    error('Acycle:Menu:Target','Expected a live MATLAB axes or figure.');
end
configured=[strsplit(engine.styles),{'operation','panel','figureIndex'}];
if ismember(engine.package,{'Robot','Desktop'}), configured{end+1}='tag'; end
bad=setdiff(fieldnames(s.plt),configured);
if ~isempty(bad), error('Acycle:Menu:PlotOption','Supply %s through dat, res or params.',bad{1}); end
targeted=~isempty(s.target) || isfield(s.plt,'panel') || isfield(s.plt,'figureIndex');
if ismember(engine.package,{'Robot','Desktop'})
    if targeted, error('Acycle:Menu:Target','Desktop commands use the running Acycle window.'); end
    [value,status]=acMenuNative(menu,engine,journal);
    return
end
p=acMenuMerge(s.params,s.dat);
if isstruct(s.res) && isscalar(s.res), p=acMenuMerge(p,s.res); end
if ~isempty(s.res), p.result=s.res; end
display=s.plt;
for name={'panel','figureIndex','operation'}
    if isfield(display,name{1}), display=rmfield(display,name{1}); end
end
p=acMenuMerge(p,display);
if isfield(p,'operation'), p=rmfield(p,'operation'); end
if ~isempty(engine.plotFields)
    % Data-dependent legacy branches may leave inactive fields absent; the original
    % renderer reads them only when selected. Never fill in missing scientific inputs.
    if strcmp(engine.package,'SimplePlot')
        missing=setdiff(strsplit(engine.plotFields),fieldnames(p));
        if ~isempty(missing), error('Acycle:Menu:MissingOption','Missing plot field %s.',missing{1}); end
    end
end
if targeted
    if ismember(engine.package,{'BispectralExport','EvolutionaryWorkbook','InsolLatDayGif'})
        error('Acycle:Menu:Target','%s writes output files and has no target axes.',engine.operation);
    end
    [value,status]=acMenuRender(engine,s,p,journal,live);
else
    [value,status]=acMenuOriginal(engine,'plotter',p,journal);
end
end
