function input = inputFor(engine,value)
% A scalar structure preserves method-specific inputs such as coordinates and units.
if isstruct(value), input = value; return; end
if ischar(value) || (isstring(value) && isscalar(value)), value = accore.io('read',value); end
fields = strsplit(engine.fields);
candidates = {'data','data_r','data_s','selectedData','dat','dataCell','im_name','I','series','data_even','data_new'};
key = find(ismember(candidates,fields),1);
if isempty(key), error('Acycle:CLI:Input','Supply the named inputs for %s in a struct.',engine.operation); end
input = struct(); input.(candidates{key}) = value;
end
