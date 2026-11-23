function s = run(tag,input,opts)
% Run one menu feature from data, an explicit input structure or a series file.
arguments
    tag
    input = struct()
    opts.Operation = ''
    opts.Params (1,1) struct = struct()
    opts.Plt (1,1) struct = struct()
    opts.Plot (1,1) logical = false
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
input = accli.inputFor(engine,input);
input.operation = engine.operation;
over = struct('params',opts.Params,'plt',opts.Plt);
ids = struct('helper',acMenuNewId(),'analyzer',[],'plotter',[]);
h = accore.run(menu.tag,'helper','input',input,'override',over,'id',ids.helper);
s = struct('tag',menu.tag,'operation',engine.operation,'input',input,'explicit',over, ...
    'params',h.params,'plt',h.plt,'dat',h.dat,'res',[],'ids',ids);
if ismember('analyzer',strsplit(engine.roles))
    s.ids.analyzer = acMenuNewId();
    accore.source(s.ids.analyzer,struct('helper',s.ids.helper));
    s.res = accore.run(s.tag,'analyzer',s.params,s.ids.analyzer);
end
if opts.Plot || ~isempty(opts.Target), s = accli.replot(s,struct(),opts.Target); end
end
