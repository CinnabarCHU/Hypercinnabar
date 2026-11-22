function [retval,id] = plotter(params,id)
% Bandpass.plotter parameters: result data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/ft.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Bandpass-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
filtered = p.result.result; data = p.data; time = data(:,1); L = numel(time); dt = median(diff(time));
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
app.AxesTop = subplot(2,1,1,'Parent',figure);
plot(app.AxesTop,f,P1,'Color',[0.2 0.65 0.95]); hold(app.AxesTop,'on');
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/ft.m:L479-L481
                plot(app.AxesTop,filtered.response_frequency, ...
                    max(P1)*filtered.response_gain,'r-');
                data_filterout = [time,filtered.filtered,filtered.envelope];
%% End copied source
subplot(2,1,2); plot(time,data_filterout(:,2),time,data_filterout(:,3));
r = [];
end
