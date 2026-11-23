function test_code_only_poc()
% Run against the assembled product with no upstream checkout on the MATLAB path.
root = setup_acycle();
savedPath = path; savedPwd = pwd; savedLog = getenv('ACYCLE_LOG_DIR');
savedVisibility = get(groot,'DefaultFigureVisible'); savedRng = rng;
hadWorkspace = ispref('AcyclePoC','Workspace');
if hadWorkspace, oldWorkspace = getpref('AcyclePoC','Workspace'); else, oldWorkspace = ''; end
folder = tempname; mkdir(folder);
cleanup = onCleanup(@()restore(folder,savedPwd,savedPath,savedLog,savedVisibility,savedRng,hadWorkspace,oldWorkspace)); %#ok<NASGU>
setenv('ACYCLE_LOG_DIR',fullfile(folder,'journal')); set(groot,'DefaultFigureVisible','off');
assert(isempty(dir(fullfile(root,'**','*.fig'))));
c = accore.register(); assert(numel(c.engines)==516 && nnz(~cellfun(@isempty,{c.menus.entry}))==118);
for k = 1:numel(c.menus)
    m = c.menus(k);
    if ~isempty(m.entry)
        [~,engine] = accore.register(m.tag);
        if ~isempty(m.guide), assert(strcmp(engine.revision,'guide'),m.tag); end
        for op = strsplit(m.choices)
            [~,item] = accore.register(m.tag,op{1}); assert(strcmp(item.operation,op{1}));
        end
    end
end
% Verify the native constructors of every old layout, including panels and tables.
layouts = dir(fullfile(root,'upstream','acycle','**','aclayout_*.m'));
assert(numel(layouts)==33);
for k = 1:numel(layouts)
    [~,name] = fileparts(layouts(k).name);
    [f,h,init] = feval(name); assert(isgraphics(f,'figure') && isstruct(h) && iscell(init)); delete(f);
end
t = (0:255)'; data = [t,sin(2*pi*t/20)+.2*cos(2*pi*t/5)];
file = fullfile(folder,'test-series.txt'); writematrix(data,file,'Delimiter','tab');
data = accore.io('read',file);
fig = ac(folder); h = acgui.state(fig);
assert(isequal(fig,ac()) && strcmp(h.menu_anova.Parent.Tag,'menu_univariate'));
assert(strcmp(h.menu_open.Parent.Tag,'menu_file') && strcmp(h.menu_bispectral.Parent.Tag,'menuac'));
assert(strcmp(h.menu_settings.Parent.Tag,'menu_help') && isgraphics(findall(fig,'Tag','push_robot')));
assert(strcmp(h.menu_multivariate1.Visible,'on') && strcmp(h.menu_pca.Parent.Tag,'menu_multivariate1'));
assert(strcmp(h.menu_open.Visible,'off') && strcmp(h.menu_opendir.Visible,'on'));
cases = {@()checkFilter(h,data,folder,t),@()checkDetrend(h,data),@()checkImage(data,folder), ...
    @()checkSwa(h),@()checkBispectral(h,data),@()checkRobot(fig,h,data,folder)};
failures = {};
for k = 1:numel(cases)
    acgui.refresh(h,folder);
    names = cellstr(h.listbox_acmain.String);
    h.listbox_acmain.Value = find(strcmp(names,'test-series.txt'));
    try
        feval(cases{k});
        fprintf('PASS %s\n',func2str(cases{k}));
    catch err
        failures{end+1} = func2str(cases{k}); %#ok<AGROW>
        fprintf(2,'FAIL %s\n%s\n',failures{end},getReport(err,'extended','hyperlinks','off'));
    end
end
screenshot = fullfile(getenv('RUNNER_TEMP'),'acycle-preview.png');
if ~isempty(getenv('RUNNER_TEMP'))
    set(fig,'Visible','on'); drawnow;
    try
        frame = getframe(fig); imwrite(frame.cdata,screenshot);
    catch
        print(fig,screenshot,'-dpng','-r100');
    end
end
assert(isempty(failures),'Cases failed: %s',strjoin(failures,', '));
fprintf('All 33 layouts, desktop selection, original filter/detrend/SWA previews, version selection, master bispectrum, exchange and replay passed.\n');
end

function checkFilter(h,data,folder,t)
click(h.menu_filter);
filter = findall(groot,'Tag','ft_figure'); assert(isscalar(filter));
s = getappdata(filter,'AcycleAnalysis'); cli = accli.filter(data);
numeric = sortrows(data); numeric(:,2) = numeric(:,2)-mean(numeric(:,2));
y = gaussfilter(numeric(:,2),mean(diff(numeric(:,1))),(s.params.flow+s.params.fhigh)/2,s.params.flow,s.params.fhigh);
assert(max(abs(s.res.data_filterout(:,2)-y(:)))<1e-10);
assert(strcmp(s.operation,'Bandpass_legacy') && isequaln(s.res,cli.res));
assert(strcmp(accli.filter(data,'Operation','Bandpass').operation,'Bandpass'));
fstate = acgui.state(filter); assert(~isempty(fstate.ft_axes3.Children) && ~isempty(fstate.ft_axes4.Children));
fstate.edit1.String = '0.041'; click(fstate.edit1); amended = getappdata(filter,'AcycleAnalysis');
assert(amended.ids.analyzer~=s.ids.analyzer && amended.params.flow==.041);
fstate.edit11.String = '0.15'; click(fstate.edit11); styleOnly = getappdata(filter,'AcycleAnalysis');
assert(styleOnly.ids.analyzer==amended.ids.analyzer && ~isequal(styleOnly.ids.plotter,amended.ids.plotter));
ax = axes('Parent',figure); sibling = axes('Parent',ancestor(ax,'figure')); line = plot(sibling,1:4);
replotted = accli.replot(amended,struct('panel','fft'),ax);
assert(replotted.ids.analyzer==amended.ids.analyzer && isgraphics(line));
[result,id] = accore.replay(amended.ids.analyzer); assert(isequaln(result,amended.res) && ~isempty(id));
changed = accli.rerun(cli,struct('flow',.04)); transferred = accli.apply(changed,[t,cos(2*pi*t/23)]);
assert(transferred.params.flow==.04 && ~isequaln(changed.dat,transferred.dat));
exchange = fullfile(folder,'exchange.mat'); accore.io('save',exchange,amended);
assert(isequaln(amended,accore.io('load',exchange)));
priorLog = getenv('ACYCLE_LOG_DIR');
restoreLog = onCleanup(@()setenv('ACYCLE_LOG_DIR',priorLog)); %#ok<NASGU>
setenv('ACYCLE_LOG_DIR',fullfile(folder,'imported-journals'));
assert(isequaln(amended.res,accore.replay(exchange,'analyzer')));
end

function checkDetrend(h,data)
click(h.menu_prewhiten); detrend = findall(groot,'Tag','gui2'); assert(isscalar(detrend));
ds = acgui.state(detrend); ds.checkbox13.Value=1; click(ds.checkbox13);
dq = getappdata(detrend,'AcycleAnalysis'); reference = accli.prewhiten(data,'Params',struct('method','polynomial','degree',3));
assert(isequaln(dq.res,reference.res));
assert(max(abs(dq.res.trend-polyval(polyfit(data(:,1),data(:,2),3),data(:,1))))<1e-10);
gapped = data; gapped(5,2) = NaN;
meanFit = accli.prewhiten(gapped,'Params',struct('method','mean'));
assert(all(meanFit.res.trend==mean(gapped(:,2),'omitnan')));
end

function checkImage(data,folder)
ax = axes('Parent',figure);
imageData = reshape(uint8(1:100),10,10);
imageSession = accli.improfile(struct('I',imageData,'CursorInfo_value',[2 2;8 8],'color_type','grayscale'));
assert(isequal(imageSession.res.data1,[2 2;8 8]) && isequaln(imageSession.res,accore.replay(imageSession.ids.analyzer)));
rgbFile = fullfile(folder,'image.png'); imwrite(repmat(imageData,1,1,3),rgbFile);
gray = accli.rgb2gray(rgbFile); assert(isequal(gray.res.I,imageData));
singlePlot = accli.plot(data,'Target',ax); assert(~isempty(singlePlot.ids.plotter));
end

function checkSwa(h)
click(h.menu_swa); fs = findall(groot,'Type','figure');
ix = arrayfun(@(g)isstruct(getappdata(g,'AcycleAnalysis')) && strcmp(getappdata(g,'AcycleAnalysis').operation,'SWA_legacy'),fs);
assert(nnz(ix)==1);
swaFig = fs(ix); sw = getappdata(swaFig,'AcycleAnalysis');
curve = findall(swaFig,'Style','checkbox','String','90% chi2 CL'); curve.Value=1; click(curve);
sw2 = getappdata(swaFig,'AcycleAnalysis'); assert(sw.ids.analyzer==sw2.ids.analyzer && sw.ids.plotter~=sw2.ids.plotter);
end

function checkBispectral(h,data)
click(h.menu_bispectral);
bs = accli.bispectral(data); assert(strcmp(bs.operation,'Bispectral') && isstruct(bs.res));
bf = findall(groot,'Tag','bispectralGUI');
inference = findall(bf,'Tag','bispectralSignificance'); inference.Value='none';
btn = findall(bf,'Tag','bispectralRun'); feval(btn.ButtonPushedFcn,btn,[]);
bq = getappdata(bf,'AcycleAnalysis'); assert(isstruct(bq) && ~isempty(bq.ids.plotter));
assert(isequaln(bq.res,accore.replay(bq.ids.analyzer)));
end

function checkRobot(fig,h,data,folder)
settings = struct('spacing',2,'trend','linear','spectrum',false,'evolutionary',false,'wavelet',true,'maxPeriod',32);
ro = accli.miniRobot(data,'Settings',settings,'Unit','m','UnitType',1);
rm = accli.robot(struct('data',data,'unit','m','unitType',1),'Operation','Robot','Params',settings);
assert(isempty(ro.res.resampled) && size(rm.res.resampled,1)<size(data,1));
assert(rm.res.maxFrequency==.25 && rm.res.minPeriod==4);
assert(~isempty(ro.res.wavelet) && isequaln(ro.res,accore.replay(ro.id)));
second = fullfile(folder,'second.txt'); writematrix(data,second,'Delimiter','tab');
acgui.refresh(h,folder);
names = cellstr(h.listbox_acmain.String);
h.listbox_acmain.Value = find(ismember(names,{'test-series.txt','second.txt'}));
click(findall(fig,'Tag','push_robot'));
assert(numel(findall(groot,'Type','figure','Name','Mini-Robot'))==2);
end

function click(obj)
cb = obj.Callback;
if iscell(cb), feval(cb{1},obj,[],cb{2:end}); else, cb(obj,[]); end
end

function restore(folder,oldPwd,oldPath,oldLog,visibility,oldRng,hadWorkspace,oldWorkspace)
delete(findall(groot,'Type','figure')); cd(oldPwd); path(oldPath); rng(oldRng);
setenv('ACYCLE_LOG_DIR',oldLog); set(groot,'DefaultFigureVisible',visibility);
if hadWorkspace, setpref('AcyclePoC','Workspace',oldWorkspace);
elseif ispref('AcyclePoC','Workspace'), rmpref('AcyclePoC','Workspace'); end
if isfolder(folder), rmdir(folder,'s'); end
end
