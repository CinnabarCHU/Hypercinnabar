function json = live(action,request)
% JSON-only boundary for the local Harness connector. Handles stay in this desktop.
q = jsondecode(request);
windowId = member(q,'window_id','');
switch char(action)
    case 'inspect'
        if isempty(windowId)
            figures = liveWindows(); items = cell(1,numel(figures));
            for k = 1:numel(figures), items{k} = snapshot(figures(k)); end
            stream = acgui.liveEvents('read',0,'');
            reply = struct('status','ok','windows',{items},'cursor',stream.cursor);
        else
            fig = lookup(windowId);
            if isempty(fig), reply = closed(windowId); else, reply = snapshot(fig); end
        end
    case 'open'
        reply = openWindow(q);
    case 'update'
        fig = lookup(windowId);
        if isempty(fig)
            reply = closed(windowId);
        else
            current = snapshot(fig);
            if ~isfield(q,'expected_revision') || current.revision~=q.expected_revision
                reply = struct('status','conflict','current',current);
            elseif ~strcmp(current.feature,'filter') || isempty(current.writable_params)
                reply = struct('status','unsupported','current',current);
            else
                try
                    acgui.filterChange(fig,member(q,'params',struct()),member(q,'plt',struct()));
                    reply = snapshot(fig);
                catch err
                    reply = struct('status','invalid','identifier',err.identifier,'message',err.message,'current',snapshot(fig));
                end
            end
        end
    case 'events'
        after = member(q,'after',0);
        validateattributes(after,{'numeric'},{'scalar','integer','nonnegative','finite'});
        reply = acgui.liveEvents('read',after,windowId);
    otherwise
        error('Acycle:GUI:Action','Unknown live GUI operation.');
end
json = jsonencode(reply);
end

function reply = openWindow(q)
feature = char(q.feature); file = char(q.input_path);
if ~isfile(file), error('Acycle:GUI:Input','Input file does not exist.'); end
[~,info] = fileattrib(file); file = info.Name;
if strcmp(feature,'image_profile')
    fig = acgui.transectWindow(file);
elseif strcmp(feature,'filter')
    windows = liveWindows();
    for k = 1:numel(windows)
        m = getappdata(windows(k),'AcycleLive');
        if ~strcmp(m.feature,'filter'), continue; end
        h = acgui.state(windows(k)); opened = member(h,'openedFrom',h.data_name);
        if strcmp(opened,file)
            figure(windows(k)); reply = snapshot(windows(k)); return;
        end
        if ~strcmp(member(q,'window_id',''),m.window_id) || member(q,'expected_revision',-1)~=m.revision
            reply = struct('status','conflict','current',snapshot(windows(k))); return;
        end
    end
    main = acgui.desktop(); h = acgui.state(main);
    [~,~,ext] = fileparts(file);
    if strcmpi(ext,'.mat')
        s = accore.io('load',file);
        if ~isstruct(s) || ~isfield(s,'operation') || ~strcmp(s.operation,'Bandpass_legacy') || isempty(s.res)
            error('Acycle:GUI:Exchange','The editable filter expects a completed Bandpass_legacy exchange.');
        end
        h.savedBandpass = s; h.current_data = s.params.data; h.data_name = member(s,'source_name',file);
        h.unit = member(s.plt,'unit',h.unit);
    else
        h.current_data = accore.io('read',file); h.data_name = file;
    end
    fig = ft(h);
    fh = acgui.state(fig); fh.openedFrom = file; acgui.state(fig,fh);
    figure(fig);
else
    error('Acycle:GUI:Feature','Unknown live window feature.');
end
reply = snapshot(fig);
end

function out = snapshot(fig)
out = getappdata(fig,'AcycleLive');
out.title = fig.Name; out.writable_params = {}; out.writable_plt = {};
s = getappdata(fig,'AcycleAnalysis');
if strcmp(out.feature,'filter')
    h = acgui.state(fig);
    out.input_path = h.data_name; out.unit = h.unit;
    out.opened_from = member(h,'openedFrom',h.data_name);
    if isstruct(s) && strcmp(s.operation,'Bandpass_legacy')
        out.params = struct('flow',s.params.flow,'fhigh',s.params.fhigh,'filter',s.params.filter);
        out.plt = struct('x_1',s.plt.x_1,'x_2',s.plt.x_2,'y_1',s.plt.y_1,'y_2',s.plt.y_2);
        out.panels = {'fft','mtm'};
        out.writable_params = {'flow','fhigh'}; out.writable_plt = fieldnames(out.plt)';
        out.export_name = h.add_list; out.result_size = size(h.data_filterout);
    end
else
    h = getappdata(fig,'AcycleTransect');
    out.input_path = h.file; out.points = h.points; out.unit = 'pixel';
    if isstruct(s), out.result_size = size(s.res.data); end
end
if isstruct(s), out.operation = s.operation; out.analysis_ids = s.ids; end
end

function figs = liveWindows()
figs = findall(groot,'Type','figure');
figs = figs(arrayfun(@(f)isappdata(f,'AcycleLive'),figs));
end

function fig = lookup(id)
fig = [];
figs = liveWindows();
for k = 1:numel(figs)
    m = getappdata(figs(k),'AcycleLive');
    if strcmp(m.window_id,id), fig = figs(k); return; end
end
end

function out = closed(id)
out = struct('status','closed','window_id',id);
end

function value = member(s,name,fallback)
if isfield(s,name), value=s.(name); else, value=fallback; end
end
