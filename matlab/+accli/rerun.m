function s = rerun(s,changes)
% Recompute from the successful scientific parameters, retaining their provenance.
[~,engine] = accore.register(s.tag,s.operation);
raw = {'operation','data','data_r','data_s','selectedData','dat','dataCell','im_name', ...
    'I','series','data_even','data_new','inputfile','input_bytes','reference','dat1','dat2'};
if ~isstruct(changes) || ~isscalar(changes) || any(ismember(fieldnames(changes),raw)) || ...
        ~all(ismember(fieldnames(changes),strsplit(engine.fields)))
    error('Acycle:CLI:Params','Use scientific option names for this operation. Use apply for new input.');
end
p = acMenuMerge(s.params,changes);
id = acMenuNewId();
accore.source(id,struct('helper',s.ids.helper,'analyzer',s.ids.analyzer));
res = accore.run(s.tag,'analyzer',p,id);
s.params = p; s.res = res;
s.ids.analyzer = id; s.ids.plotter = [];
s.explicit.params = acMenuMerge(s.explicit.params,changes);
end
