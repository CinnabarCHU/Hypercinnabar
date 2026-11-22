function [retval,id] = analyzer(params,id)
% EvolutionarySpectrum.analyzer parameters: data window step fmin nyquist normal method time_0pad padtype mean_step.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/evofftGUI.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('EvolutionarySpectrum-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data; window = p.window; step = p.step; fmin = p.fmin; app = p;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/evofftGUI.m:L699-L717
            if app.time_0pad == 1
                data = zeropad2(data,window,app.padtype);
            else
                data(:,2) = data(:,2) - mean(data(:,2));
            end

            if strcmp(app.method,'Periodogram')
                [s,x_grid,y_grid] = evoperiodogram(data,window,step,fmin,app.nyquist,app.normal);
            elseif strcmp(app.method,'Lomb-Scargle periodogram')
                [s,x_grid,y_grid] = evoplomb(data,window,step,fmin,app.nyquist,app.normal);
            elseif strcmp(app.method,'Multi-taper method')
                [s,x_grid,y_grid] = evopmtm(data,window,step,fmin,app.nyquist,app.normal);
            elseif strcmp(app.method,'Fast Fourier transform (MatLab)')
                [s,x_grid,y_grid] = evofftML(data,window,step, ...
                    fmin,app.nyquist,app.normal);
            else
                dt = app.mean_step;
                [s,x_grid,y_grid] = evofft(data,window,step,dt,fmin,app.nyquist,app.normal);
            end
%% End copied source
r = struct();
r.s = s;
r.x_grid = x_grid;
r.y_grid = y_grid;
end
