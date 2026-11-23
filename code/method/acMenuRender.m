function [value,status] = acMenuRender(engine,s,p,journal,target)
% Render using upstream code, then move a complete figure or one panel into its host.
before=findall(groot,'Type','figure');
previous=get(groot,'CurrentFigure');
visibility=get(groot,'DefaultFigureVisible');
names=cell(0,3);
persistent sequence
if isempty(sequence), sequence=0; end
sequence=sequence+1;
if ismember(engine.package,{'OneSampleT','SWA','ColumnManipulation','DataTransform','LinearRegression'})
    for k=1:numel(before)
        f=before(k);
        if startsWith(f.Name,'Acycle') || strcmp(f.Tag,'fig_data_transf')
            names(end+1,:)={f,f.Name,f.Tag}; %#ok<AGROW>
            f.Name=sprintf('acMenuRender_%d_%d',sequence,k); f.Tag='';
        end
    end
end
createdTarget=[];
keepTarget=false;
cleanup=onCleanup(@restoreFigures);
set(groot,'DefaultFigureVisible','off');
figure('Visible','off','HandleVisibility','on');
[value,status]=acMenuOriginal(engine,'plotter',p,journal);
figs=flipud(findall(groot,'Type','figure'));
figs=figs(~ismember(figs,before));
keep=false(size(figs));
for k=1:numel(figs), keep(k)=~isempty(figs(k).Children); end
figs=figs(keep);
if isempty(figs), error('Acycle:Menu:Target','This call produced no transferable figure.'); end
if isfield(s.plt,'figureIndex')
    index=s.plt.figureIndex;
    if ~(isnumeric(index) && isscalar(index) && ismember(index,1:numel(figs)))
        error('Acycle:Menu:FigureIndex','Invalid plot figure index.');
    end
    figs=figs(index);
end
panel=[];
if isfield(s.plt,'panel'), panel=s.plt.panel; end
if isempty(s.target)
    if isempty(panel), kind='figure'; else, kind='axes'; end
else
    kind=s.target.kind;
end
if strcmp(kind,'figure') && numel(figs)>1 && isempty(panel)
    error('Acycle:Menu:FigureIndex','Set plt.figureIndex to select one of %d figures.',numel(figs));
end
if strcmp(kind,'axes') || ~isempty(panel)
    axesList=gobjects(0,1);
    for k=1:numel(figs)
        group=findall(figs(k),'Type','axes');
        positions=zeros(numel(group),2);
        for j=1:numel(group)
            pos=getpixelposition(group(j),true);
            positions(j,:)=[-(pos(2)+pos(4)/2),pos(1)];
        end
        [~,order]=sortrows(positions,[1 2]);
        axesList=[axesList;group(order)]; %#ok<AGROW>
    end
    if isempty(panel) && numel(axesList)==1, panel=1; end
    if ischar(panel) || (isstring(panel) && isscalar(panel))
        panel=find(arrayfun(@(a)strcmp(a.Tag,panel),axesList));
    end
    if ~(isnumeric(panel) && isscalar(panel) && ismember(panel,1:numel(axesList)))
        error('Acycle:Menu:Panel','Select one of %d axes with plt.panel (index or unique tag).',numel(axesList));
    end
    source=axesList(panel);
end
if isempty(target)
    createdTarget=figure('Visible',visibility);
    if strcmp(kind,'axes'), target=axes('Parent',createdTarget); else, target=createdTarget; end
end
if strcmp(kind,'axes')
    acMenuCopyAxes(source,target);
else
    if ~isempty(panel)
        children=copyobj(source,target);
        colormap(children,colormap(source));
    else
        % Copy related axes, legends and colorbars together, preserving associations.
        children=copyobj(flipud(figs(1).Children),target);
        for i=1:numel(children)
            if isgraphics(children(i),'axes'), colormap(children(i),colormap(figs(1))); end
        end
    end
    if isappdata(target,'acMenuRenderedChildren')
        old=getappdata(target,'acMenuRenderedChildren'); delete(old(isgraphics(old)));
    end
    setappdata(target,'acMenuRenderedChildren',children);
end
keepTarget=true;
clear cleanup

    function restoreFigures()
        allFigs=findall(groot,'Type','figure');
        remove=~ismember(allFigs,before);
        if keepTarget && ~isempty(createdTarget), remove=remove & allFigs~=createdTarget; end
        delete(allFigs(remove));
        for i=1:size(names,1)
            if isgraphics(names{i,1}), set(names{i,1},'Name',names{i,2},'Tag',names{i,3}); end
        end
        set(groot,'DefaultFigureVisible',visibility);
        if ~isempty(previous) && isgraphics(previous), set(groot,'CurrentFigure',previous); end
    end
end

function acMenuCopyAxes(source,target)
% Keep the host axes identity, its layout, and all sibling axes intact.
old=target.Children;
copied=gobjects(0);
try
    copied=copyobj(flipud(source.Children),target);
    for key={'XScale','YScale','ZScale','XDir','YDir','ZDir','View','Box','Color', ...
            'XMinorTick','YMinorTick','ZMinorTick','XGrid','YGrid','ZGrid','CLim','XLim','YLim','ZLim', ...
            'ColorScale','Projection','LineWidth','Visible','TickDir'}
        target.(key{1})=source.(key{1});
    end
    for key={'XTick','YTick','ZTick','XTickLabel','YTickLabel','ZTickLabel', ...
            'DataAspectRatio','PlotBoxAspectRatio'}
        prop=key{1};
        if strcmp(source.([prop,'Mode']),'manual'), target.(prop)=source.(prop);
        else, target.([prop,'Mode'])='auto'; end
    end
    for key={'Title','XLabel','YLabel','ZLabel'}
        src=source.(key{1}); dst=target.(key{1});
        set(dst,'Interpreter',src.Interpreter,'String',src.String,'Color',src.Color);
    end
    colormap(target,colormap(source));
catch err
    delete(copied(isgraphics(copied)));
    rethrow(err)
end
delete(old(isgraphics(old)));
if isprop(source,'Legend') && ~isempty(source.Legend) && isgraphics(source.Legend)
    legend(target,source.Legend.String,'Location',source.Legend.Location,'Interpreter',source.Legend.Interpreter);
end
if isprop(source,'Colorbar') && ~isempty(source.Colorbar) && isgraphics(source.Colorbar)
    bar=colorbar(target,'Location',source.Colorbar.Location);
    bar.Label.String=source.Colorbar.Label.String;
end
end
