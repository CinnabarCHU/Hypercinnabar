function s = run(tag,input,opts)
% Run one menu feature from data, an explicit input structure or a series file.
arguments
    tag
    input = struct()
    opts.Operation = ''
    opts.Params (1,1) struct = struct()
    opts.Plt (1,1) struct = struct()
    opts.Plot = []
    opts.Target = []
end
if isfield(opts.Params,'operation')
    if ~isempty(opts.Operation) && ~strcmp(opts.Operation,opts.Params.operation)
        error('Acycle:CLI:Operation','Two different operations were requested.');
    end
    opts.Operation = opts.Params.operation;
    opts.Params = rmfield(opts.Params,'operation');
end
if isstruct(input) && isfield(input,'operation') && isempty(opts.Operation)
    opts.Operation = input.operation;
end
[menu,engine] = accore.register(tag,opts.Operation);
if ~isempty(menu.workflow) && (~isstruct(input) || isfield(input,'data'))
    if ~isempty(opts.Target) || ~isempty(fieldnames(opts.Plt))
        error('Acycle:CLI:RobotPlot','Mini-Robot manages several figures. Select Plot to display them.');
    end
    meta = {};
    if isstruct(input)
        for key = {'Name','Unit','UnitType'}
            field = key{1}; field(1) = lower(field(1));
            if isfield(input,field), meta = [meta,key,{input.(field)}]; end %#ok<AGROW>
        end
        input = input.data;
    end
    s = accli.miniRobot(input,'Operation',engine.operation,'Settings',opts.Params, ...
        'Plot',~isempty(opts.Plot) && opts.Plot,meta{:});
    return
end
input = accli.inputFor(engine,input);
input.operation = engine.operation;
over = struct('params',opts.Params,'plt',opts.Plt);
ids = struct('helper',acMenuNewId(),'analyzer',[],'plotter',[]);
h = accore.run(menu.tag,'helper','input',input,'override',over,'id',ids.helper);
raw = {'operation','data','data_r','data_s','data_even','data_new','data_filterout','selectedData', ...
    'dat','dat1','dat2','dataCell','im_name','I','image','series','reference','inputfile','input_bytes','result','CursorInfo_value'};
science = setdiff(intersect(fieldnames(input),strsplit(engine.fields)),raw);
styles = setdiff(intersect(fieldnames(input),strsplit(engine.styles)),{'filename','dat_name','color_type'});
explicit = struct('params',acMenuMerge(keep(input,science),opts.Params), ...
    'plt',acMenuMerge(keep(input,styles),opts.Plt));
s = struct('tag',menu.tag,'operation',engine.operation,'input',input,'explicit',explicit, ...
    'params',h.params,'plt',h.plt,'dat',h.dat,'res',[],'ids',ids);
if ismember('analyzer',strsplit(engine.roles))
    s.ids.analyzer = acMenuNewId();
    accore.source(s.ids.analyzer,struct('helper',s.ids.helper));
    s.res = accore.run(s.tag,'analyzer',s.params,s.ids.analyzer);
end
plot = opts.Plot;
if isempty(plot), plot = isempty(s.ids.analyzer) && ismember('plotter',strsplit(engine.roles)); end
if plot || ~isempty(opts.Target), s = accli.replot(s,struct(),opts.Target); end
end

function out = keep(s,keys)
out = rmfield(s,setdiff(fieldnames(s),keys));
end
