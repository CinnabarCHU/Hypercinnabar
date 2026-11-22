function [retval,id] = analyzer(params,id)
% AstronomicalSolution.analyzer parameters: solution parameter t1 t2; ETP weights.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/basicseries.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('AstronomicalSolution-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
solution = p.solution; app.t1=p.t1; app.t2=p.t2; app.parameterKey=p.parameter;
app.dataDir=fileparts(which('La04.mat'));
app.loadDataFile=@(name) loadDataFile(app,name);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/basicseries.m:L310-L332
            ref = 0;
            dat = [];

            switch solution
                case 'La2004'
                    dat = app.loadDataFile('La04.mat');
                    ref = 1;
                case 'La2010a'
                    dat = app.loadDataFile('La10a.mat');
                    ref = 2;
                case 'La2010b'
                    dat = app.loadDataFile('La10b.mat');
                    ref = 2;
                case 'La2010c'
                    dat = app.loadDataFile('La10c.mat');
                    ref = 2;
                case 'La2010d'
                    dat = app.loadDataFile('La10d.mat');
                    ref = 2;
                case 'ZB18a'
                    dat = app.loadDataFile('ZB18a.dat');
                    ref = 4;
            end
%% End copied source
if isempty(dat), error('Acycle:Orbit:Unavailable','Orbit table not available for %s.',solution); end
app.basicdata = dat; app.refType=ref;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/basicseries.m:L436-L452
            t1 = min(app.t1, app.t2);
            t2 = max(app.t1, app.t2);

            if t1 < 0
                error('Error: t1 must be no less than 0');
            end
            if t2 <= t1
                error('Error: t2 must be larger than t1');
            end
            if app.refType == 4 && t2 > 1.0e5
                error('Error: t2 must be less than 100,000');
            end
            if (app.refType == 1 || app.refType == 2) && t2 >= 249000
                error('Error: t2 must be less than 249,000');
            end

            data = select_interval(app.basicdata, t1, t2);
%% End copied source
switch p.parameter
case 'ETP'
    if ~ismember(ref,[1 2]), error('Acycle:Orbit:Parameter','Requested solution has no ETP.'); end
    wE=p.weights(1); wT=p.weights(2); wP=p.weights(3);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/basicseries.m:L458-L459
                data(:,5) = wE * zscore(data(:,2)) + wT * zscore(data(:,3)) + wP * zscore(data(:,4));
                dat = [data(:,1), data(:,5)];
%% End copied source
case 'Eccentricity'
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/basicseries.m:L466-L466
                dat = [data(:,1), data(:,2)];
%% End copied source
case 'Obliquity'
    if ~ismember(ref,[1 2]), error('Acycle:Orbit:Parameter','Requested solution has no obliquity.'); end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/basicseries.m:L469-L469
                dat = [data(:,1), data(:,3)];
%% End copied source
case 'Precession'
    if ~ismember(ref,[1 2]), error('Acycle:Orbit:Parameter','Requested solution has no precession.'); end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/basicseries.m:L472-L472
                dat = [data(:,1), data(:,4)];
%% End copied source
case 'Inclination'
    if ref~=4, error('Acycle:Orbit:Parameter','Inclination requires ZB18a.'); end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/basicseries.m:L475-L475
                dat = [data(:,1), data(:,3)];
%% End copied source
otherwise, error('Acycle:Orbit:Parameter','Unknown orbital parameter.');
end
r = dat;
end

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/basicseries.m:L355-L377
        function dat = loadDataFile(app, fileName)
            dat = [];
            fullName = fullfile(app.dataDir, fileName);
            if ~isfile(fullName)
                warning(['Missing file: ', fullName]);
                return
            end

            [~,~,ext] = fileparts(fullName);
            if strcmpi(ext,'.mat')
                s = load(fullName);
                if isfield(s,'data')
                    dat = s.data;
                else
                    fns = fieldnames(s);
                    if ~isempty(fns)
                        dat = s.(fns{1});
                    end
                end
            else
                dat = load(fullName);
            end
        end
%% End copied source
