function test_menu_interfaces()
% Exercise both snapshots through the menu ABI, including failures and isolated replays.
setup_migration;
catalog=acMenuCatalog();
count=0;
for k=1:numel(catalog.menus)
    m=catalog.menus(k);
    if isempty(m.roles), continue; end
    for role=strsplit(m.roles)
        name=[m.entry,'_',role{1}];
        assert(~isempty(which(name)) && nargout(name)==1,name);
        count=count+1;
    end
end
assert(numel(catalog.menus)==136 && count==330);
original=0;
for k=1:numel(catalog.engines)
    e=catalog.engines(k);
    assert(endsWith(e.operation,'_legacy')==strcmp(e.revision,'guide'));
    if ismember(e.operation,{'Robot','Robot_legacy','Desktop_legacy'}), continue; end
    ns='acmaster'; if strcmp(e.revision,'guide'), ns='acmethods'; end
    for role=strsplit(e.roles)
        assert(~isempty(which([ns,'.',e.package,'.',role{1}])),e.operation);
        original=original+1;
        if strcmp(role{1},'analyzer') && ~isempty(e.required)
            acMenuExpect(@()acMenuValidate(e,struct()),'Acycle:Menu:MissingOption');
        end
    end
end
assert(original==789);
x=(0:127)'; data=[x,cos(2*pi*x/16)+0.2*sin(2*pi*x/7)];
for ver={'SeriesSound','SeriesSound_legacy'}
    id=acMenuNewId();
    h=acMenuSound_helper('input',struct('data',data),'override',struct('params',struct('operation',ver{1},'a',2)),'id',id);
    assert(isequal(sort(fieldnames(h)),{'dat';'params';'plt'}) && h.params.a==2);
    assert(isequaln(aclog.replay(id),h));
    n=acMenuNewId(); r=acMenuSound_analyzer(h.params,n);
    plain=rmfield(h.params,'operation');
    if endsWith(ver{1},'_legacy'), direct=acmethods.SeriesSound.analyzer(plain);
    else, direct=acmaster.SeriesSound.analyzer(plain); end
    assert(isequaln(r,direct) && isequaln(r,aclog.replay(n)));
    missing=rmfield(h.params,'a'); badId=acMenuNewId();
    acMenuExpect(@()acMenuSound_analyzer(missing,badId),'Acycle:Menu:MissingOption');
    journal=fileread(aclog.interfaceId(badId,true));
    assert(contains(journal,'"attr":"error"') && contains(journal,'"status":"cancelled"'));
    acMenuExpect(@()acMenuSound_analyzer(h.params,n),'Acycle:Logger:Reuse');
end
acMenuExpect(@()acMenuSound_helper('input',struct('data',data),'override',struct('dat',struct())),'Acycle:Menu:Override');
acMenuExpect(@()acMenuSound_analyzer(struct('data',data)),'Acycle:Menu:MissingOption');
acMenuExpect(@()acMenuSound_analyzer(struct('operation','Bandpass')),'Acycle:Menu:Operation');
acMenuExpect(@()acMenuSound_analyzer(struct('override',struct())),'Acycle:Menu:Override');
acMenuExpect(@()acMenuImshow_plotter('override',struct()),'Acycle:Menu:Arguments');
provisional=evalc('acMenuSound_helper(''input'',struct(''data'',data),''id'',-3);');
assert(contains(provisional,'"attr":"init"') && contains(provisional,'"attr":"fin"') && contains(provisional,'"id":'));
% A GUIDE helper delegates to another historical helper; both share the public record.
base=aclog.interfaceId(acMenuNewId(),true);
logRoot=fileparts(fileparts(fileparts(base)));
beforeLogs=numel(dir(fullfile(logRoot,'**','events.jsonl')));
acMenuFilter_helper(struct('data',data,'operation','PassFilter_legacy'),'id',acMenuNewId());
assert(numel(dir(fullfile(logRoot,'**','events.jsonl')))==beforeLogs+1);
% Two distinct interpolation interfaces remain available from the same menu.
a=acMenuInterp_helper(struct('data',data),'id',acMenuNewId());
assert(a.params.interpolate_rate==1 && strcmp(a.params.operation,'interpolate'));
a=acMenuInterp_helper(struct('data',data,'operation','interpolate_legacy'),'id',acMenuNewId());
assert(isequaln(acMenuInterp_analyzer(a.params,acMenuNewId()),acmethods.interpolate.analyzer(rmfield(a.params,'operation'))));
b=acMenuInterp_helper(struct('data',[data,x.^2],'samplingInterval',2,'operation','RegularInterpolation'), ...
    'override',struct('params',struct('options',struct('MaximumPoints',800))),'id',acMenuNewId());
assert(b.params.options.MaximumPoints==800 && isfield(b.params.options,'MaximumElements'));
r=acMenuInterp_analyzer(b.params,acMenuNewId()); assert(size(r.interpolated,2)==3 && isfield(r,'meta'));
b.params.options=rmfield(b.params.options,'MaximumElements');
acMenuExpect(@()acMenuInterp_analyzer(b.params,acMenuNewId()),'Acycle:Menu:MissingOption');
for selector={'PowerSpectrum','PowerSpectrum_legacy'}
    h=acMenuPower_helper(struct('data',data,'operation',selector{1}),'id',acMenuNewId());
    if endsWith(selector{1},'_legacy')
        bad=rmfield(h.params,'noise');
    else
        h=acMenuPower_helper('input',struct('data',data),'override',struct('params',struct('nfft',256)),'id',acMenuNewId());
        assert(h.params.nfft==256 && isfield(h.plt,'logFrequency') && h.params.models.robust);
        bad=rmfield(h.params,'fitModel');
    end
    acMenuExpect(@()acMenuPower_analyzer(bad,acMenuNewId()),'Acycle:Menu:MissingOption');
end
h=acMenuDigitizer_helper(struct('operation','DigitizeTrace','image',zeros(8),'seeds',[3 4], ...
    'existingPixels',[2 3],'mode','Strict','calibration',struct()),'id',acMenuNewId());
assert(strcmp(h.params.mode,'Strict') && isequal(h.params.existingPixels,[2 3]));
% A fixed user's seed is repeatable even for differing versioned return layouts.
for v={'SeriesGenerator','SeriesGenerator_legacy'}
    inp=struct('operation',v{1},'x',x,'kind','red','alpha',0.4);
    if endsWith(v{1},'_legacy'), inp.mean=0; inp.std=1; else, inp.mu=0; inp.sigma=1; end
    prep=acMenuNewId(); h=acMenuLinegenerator_helper(inp,'id',prep);
    assert(isfield(h.params,'seed') && isequaln(h,aclog.replay(prep)));
    bad=rmfield(h.params,'seed');
    acMenuExpect(@()acMenuLinegenerator_analyzer(bad,acMenuNewId()),'Acycle:Menu:MissingOption');
    id=acMenuNewId(); r=acMenuLinegenerator_analyzer(h.params,id);
    state=rng;
    randn('state',h.params.seed); %#ok<RAND>
    expected=zscore(filter(1,[1;-inp.alpha],randn(numel(x),1)));
    rng(state);
    if endsWith(v{1},'_legacy'), assert(isequal(r.x,x) && isequal(r.y,expected));
    else, assert(isequal(r,[x,expected])); end
    repeated=aclog.replay(id);
    assert(isequaln(r,repeated),'%s changed on replay.',v{1});
    assert(isequaln(rng,state),'%s replay changed the caller RNG.',v{1});
end
% Plot into the requested axes. Check the panel data and the live host separately.
visibility=get(groot,'DefaultFigureVisible'); set(groot,'DefaultFigureVisible','off');
before=findall(groot,'Type','figure');
clean=onCleanup(@()acMenuTestFigures(before,visibility)); %#ok<NASGU>
fig=figure('Visible','off'); a1=subplot(1,2,1,'Parent',fig); a2=subplot(1,2,2,'Parent',fig);
sentinel=plot(a2,[4 7]); im=uint8(reshape(mod(1:90,255),[5 6 3]));
for v={'RGBToGray','RGBToGray_legacy'}
    h=acMenuRgb2gray_helper(struct('operation',v{1},'im_name',im),'id',acMenuNewId());
    r=acMenuRgb2gray_analyzer(h.params,acMenuNewId());
    n=acMenuNewId(); acMenuRgb2gray_plotter(h.plt,'dat',h.dat,'res',r,'params',h.params,'target',a1,'id',n);
    pixels=findobj(a1,'Type','image');
    assert(isscalar(pixels) && isequal(pixels.CData,r.I) && isgraphics(sentinel));
    assert(numel(findall(groot,'Type','figure'))==numel(before)+1);
    pathId=aclog.interfaceId(n,true); lines=splitlines(string(fileread(pathId)));
    entry=jsondecode(lines(1)); request=aclog.read(pathId,entry.info.params);
    assert(any(cellfun(@(v)isstruct(v) && isfield(v,'kind') && strcmp(v.kind,'axes'),request.args)));
    aclog.replay(n);
    extra=setdiff(findall(groot,'Type','figure'),[fig;before]);
    assert(isscalar(extra) && isscalar(findobj(extra,'Type','image'))); delete(extra);
end
h=acMenuRgb2lab_helper(struct('im_name',im),'id',acMenuNewId());
r=acMenuRgb2lab_analyzer(h.params,acMenuNewId());
figureCount=numel(findall(groot,'Type','figure'));
acMenuExpect(@()acMenuRgb2lab_plotter(h.plt,'res',r,'target',a1,'id',acMenuNewId()),'Acycle:Menu:Panel');
assert(numel(findall(groot,'Type','figure'))==figureCount && isgraphics(sentinel));
h.plt.panel=2; acMenuRgb2lab_plotter(h.plt,'res',r,'target',a1,'id',acMenuNewId());
assert(strcmp(a1.Title.String,'a*') && isequal(findobj(a1,'Type','image').CData,r.I(:,:,2)) && isgraphics(sentinel));
f=figure('Visible','off'); acMenuRgb2lab_plotter(rmfield(h.plt,'panel'),'res',r,'target',f,'id',acMenuNewId());
assert(numel(findall(f,'Type','axes'))==3);
acMenuRgb2lab_plotter(rmfield(h.plt,'panel'),'res',r,'target',f,'id',acMenuNewId());
assert(numel(findall(f,'Type','axes'))==3);
badPlot=h.plt; badPlot.I=zeros(5);
acMenuExpect(@()acMenuRgb2lab_plotter(badPlot,'res',r,'target',a1,'id',acMenuNewId()),'Acycle:Menu:PlotOption');
q=acMenuCatalog('menu_timeOpt'); assert(strcmp(q.default,'TimeOpt_legacy') && isempty(q.master));
q=acMenuCatalog('menu_swa'); assert(ismember('SWA',strsplit(q.choices)));
acMenuExpect(@()acMenuSwa_analyzer(struct('operation','SWA'),acMenuNewId()),'Acycle:Menu:Role');
acMenuExpect(@()acMenuRobot_plotter(struct('operation','Robot'),'id',acMenuNewId()),'Acycle:Desktop:Session');
acMenuExpect(@()acMenuRobot_plotter(struct('operation','Robot_legacy'),'id',acMenuNewId()),'Acycle:Desktop:Session');
fprintf('Verified 330 public files, 789 prior roles, both revisions, strict parameters, graphics targets and replay.\n');
end

function acMenuExpect(call,identifier)
try
    call();
catch err
    assert(strcmp(err.identifier,identifier),'Expected %s, saw %s: %s',identifier,err.identifier,err.message);
    return
end
error('Test:Menu:ExpectedError','Expected %s.',identifier);
end

function acMenuTestFigures(before,visibility)
nowOpen=findall(groot,'Type','figure'); delete(nowOpen(~ismember(nowOpen,before)));
set(groot,'DefaultFigureVisible',visibility);
end
