function h = acMenuPrepare(menu,input,override,journal)
% Resolve the menu's original recommendations and keep settings separate from plot data.
bad=setdiff(fieldnames(override),{'params','plt'});
if ~isempty(bad), error('Acycle:Menu:Override','Unknown override branch %s.',bad{1}); end
changes=struct(); display=struct();
if isfield(override,'params'), changes=acMenuMerge(changes,override.params); end
if isfield(override,'plt'), display=acMenuMerge(display,override.plt); end
selector=menu.default;
if isfield(input,'operation'), selector=input.operation; input=rmfield(input,'operation'); end
if isfield(changes,'operation'), selector=changes.operation; changes=rmfield(changes,'operation'); end
engine=acMenuEngine(menu,selector);
names=strsplit(engine.fields);
plotNames=strsplit(engine.plotFields);
styleNames=strsplit(engine.styles);
raw={'data','dat','data_s','data_new','data_filterout','selectedData','dataCell','series','reference', ...
     'image','I','im_name','inputfile','input_bytes','data_r','data_even','dat1','dat2','result'};
illegal=intersect(fieldnames(changes),raw);
if ~isempty(illegal), error('Acycle:Menu:Override','Supply %s through input.',illegal{1}); end
bad=setdiff(fieldnames(changes),names);
if ~isempty(bad), error('Acycle:Menu:Override','Unknown scientific option %s.',bad{1}); end
input=acMenuMerge(input,changes);
recommend=struct();
if ismember('helper',strsplit(engine.roles))
    [recommend,~]=acMenuOriginal(engine,'helper',input,journal);
end
values=input;
for key=fieldnames(recommend)'
    name=key{1};
    if isfield(input,name) && isstruct(recommend.(name)) && isscalar(recommend.(name)) && ...
            isstruct(input.(name)) && isscalar(input.(name))
        values.(name)=acMenuMerge(recommend.(name),input.(name));
    elseif isfield(input,name) && ismember(name,names) && ~ismember(name,raw)
        values.(name)=input.(name);
    else
        values.(name)=recommend.(name);
    end
end
% Reuse the pinned display recommendations using the values actually selected.
if strcmp(engine.operation,'PowerSpectrum') && isfield(values,'fmin') && isfield(values,'fmax')
    [settings,~]=acMenuOriginal(engine,'helper',struct('result',values),journal);
    values=acMenuMerge(values,rmfield(settings,'result'));
elseif strcmp(engine.operation,'Bispectral') && isfield(values,'options') && ~isfield(values,'settings')
    view=acMenuEngine(menu,'BispectralView');
    [settings,~]=acMenuOriginal(view,'helper',struct('result',struct('Options',values.options)),journal);
    values.settings=settings.settings;
end
if strcmp(engine.package,'interpolate') && isfield(values,'data') && ~isfield(values,'interpolate_rate')
    data=values.data;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3235-L3236
                time = data(:,1);
                srmedian = median(diff(time));
%% End copied source
    values.interpolate_rate=srmedian;
end
if strcmp(engine.package,'SimplePlot')
    values.standardized=~strcmp(menu.tag,'menu_plot');
    values.offset=strcmp(menu.tag,'menu_plotn2');
    if ~isfield(values,'unit'), values.unit=''; end
end
h=struct('params',struct('operation',engine.operation),'plt',struct('operation',engine.operation),'dat',struct());
for key=fieldnames(values)'
    name=key{1};
    science=ismember(name,names); style=ismember(name,styleNames);
    if science, h.params.(name)=values.(name); end
    if style
        h.plt.(name)=values.(name);
    elseif ~science || ismember(name,plotNames)
        h.dat.(name)=values.(name);
    end
end
if ismember('unit',styleNames) && ~isfield(h.plt,'unit'), h.plt.unit=''; end
if strcmp(engine.package,'Desktop') || strcmp(engine.package,'Robot'), h.plt.tag=menu.tag; end
% The historical BispectralView helper owns display defaults for the Bispectral renderer.
if strcmp(engine.package,'BispectralView') && isfield(values,'settings')
    h.plt.settings=values.settings;
    h.plt.operation='Bispectral';
    if isfield(h.dat,'settings'), h.dat=rmfield(h.dat,'settings'); end
end
bad=setdiff(fieldnames(display),[styleNames {'panel','figureIndex'} fieldnames(h.plt)']);
if ~isempty(bad), error('Acycle:Menu:Override','Unknown display option %s.',bad{1}); end
if isfield(display,'operation'), error('Acycle:Menu:Override','Select the operation in params.'); end
h.plt=acMenuMerge(h.plt,display);
end
