function session = miniRobot(data,options)
% Single-series Mini-Robot with the desktop's scientific defaults.
arguments
    data
    options.Operation = 'Robot_legacy'
    options.Settings (1,1) struct = struct()
    options.Name = 'series'
    options.Unit = 'unit'
    options.UnitType = 0
    options.Plot (1,1) logical = false
    options.Save (1,1) logical = false
    options.Folder = ''
end
if ischar(data) || (isstring(data) && isscalar(data))
    if strcmp(options.Name,'series'), [~,options.Name] = fileparts(data); end
    data = accore.io('read',data);
end
if ~isnumeric(data) || ~ismatrix(data) || size(data,2)<2 || size(data,1)<3
    error('Acycle:Robot:Data','Mini-Robot requires a series with at least three samples.');
end
x = data(:,1);
dt = mean(diff(sort(x)),'omitnan'); duration = max(x,[],'omitnan')-min(x,[],'omitnan');
defaults = struct('reportNaN',true,'removeInf',true,'sort',true,'unique',true, ...
    'interpolate',true,'detrend',true,'spectrum',true,'evolutionary',true,'wavelet',false, ...
    'spacing',dt,'trend','lowess','spanPercent',35,'spectrumMethod',1, ...
    'maxFrequency',1/(2*dt),'window',.35*duration,'minPeriod',2*dt,'maxPeriod',duration);
bad = setdiff(fieldnames(options.Settings),fieldnames(defaults));
if ~isempty(bad), error('Acycle:Robot:Settings','Unknown setting %s.',bad{1}); end
settings = acMenuMerge(defaults,options.Settings);
p = struct('operation',options.Operation,'data',data,'name',options.Name,'unit',options.Unit, ...
    'unitType',options.UnitType,'settings',settings);
host = struct('plot',options.Plot,'save',options.Save);
if ~isempty(options.Folder), host.folder = options.Folder; end
id = acMenuNewId();
session = struct('params',p,'res',accore.run('push_robot','workflow',p,id,host),'id',id);
end
