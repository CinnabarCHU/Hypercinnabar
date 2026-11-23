function input = inputFor(engine,value)
% A scalar structure preserves method-specific inputs such as coordinates and units.
if isstruct(value), input = value; return; end
fields = strsplit(engine.fields);
file = '';
label = 'Series'; ext = '';
if ischar(value) || (isstring(value) && isscalar(value))
    file = char(value);
    [~,label,ext] = fileparts(file);
    if ismember('inputfile',fields)
        input = struct('inputfile',file);
        return
    end
end
candidates = {'data','data_r','data_s','selectedData','dat','dataCell','im_name','image','I','series','data_even','data_new','data_filterout'};
key = find(ismember(candidates,fields),1);
if isempty(key), key = find(ismember(candidates,strsplit(engine.plotFields)),1); end
if isempty(key), error('Acycle:CLI:Input','Supply the named inputs for %s in a struct.',engine.operation); end
field = candidates{key};
if ~isempty(file)
    if ismember(field,{'im_name','image','I'}), value = accore.io('readImage',file);
    else, value = accore.io('read',file); end
end
input = struct();
if strcmp(engine.package,'SimplePlot')
    if ~iscell(value), value = {value}; end
    input.plot_list = {label};
    if numel(value)>1, input.plot_list = arrayfun(@(k)sprintf('Series %d',k),1:numel(value),'UniformOutput',false); end
elseif ismember(engine.package,{'DataDistribution','SamplingRate'})
    input.dat_name = label; input.ext = ext; input.unit = 'unit'; input.unit_type = 0;
end
input.(field) = value;
end
