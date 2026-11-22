function [retval,id] = helper(params,id)
% Bandpass.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/ft.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Bandpass-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/ft.m:L101-L115
            if ~((isa(data,'double') || isa(data,'single')) && ...
                    isreal(data) && ismatrix(data) && size(data,2) == 2 && ...
                    ~issparse(data))
                error('Acycle:FT:InvalidInputSeries', ...
                    'Filtering requires a real floating-point N-by-2 series.');
            end
            data = double(data(all(isfinite(data),2),:));
            data = sortrows(data,1);
            data = findduplicate(data);
            if size(data,1) < 8
                error('Acycle:FT:InsufficientFiniteData', ...
                    ['Filtering requires at least eight finite samples ', ...
                     'after duplicate coordinates are combined.']);
            end
            if acycleSamplingIsUneven(data(:,1))
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/ft.m:L118-L131
                data = interpolate(data,median(diff(data(:,1))));
            end
            dt = median(diff(data(:,1)));
            valueScale = max(abs(data(:,2)));
            if valueScale == 0
                inputMean = 0;
            else
                inputMean = valueScale*mean(data(:,2)/valueScale);
            end
            data(:,2) = data(:,2)-inputMean;
            if any(~isfinite(data(:,2))) || all(data(:,2) == 0)
                error('Acycle:FT:InvalidInputVariance', ...
                    'The value column must have representable positive variance.');
            end
%% End copied source
L = size(data,1);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/ft.m:L376-L384
            Y = fft(data(:,2),L);
            P2 = abs(Y/L);
            P1 = P2(1:floor(L/2)+1);
            if mod(L,2) == 0
                P1(2:end-1) = 2*P1(2:end-1);
            else
                P1(2:end) = 2*P1(2:end);
            end
            f = (0:floor(L/2))'/(L*dt);
%% End copied source
app.P1 = P1;
app.f_fft = f;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/ft.m:L337-L341
            [~,idx] = max(app.P1);
            fq = app.f_fft(idx);
            app.filt_fmid = fq;
            app.filt_flow = fq*0.8;
            app.filt_fhigh = fq*1.2;
%% End copied source
r = struct('data',data,'options',struct('method','gaussian', ...
    'lower_frequency',app.filt_flow,'upper_frequency',app.filt_fhigh));
end
