function [retval,id] = analyzer(params,id)
% BuildAgeModel.analyzer parameters: data period pkstrough.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('BuildAgeModel-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
period = p.period;
pkstrough = p.pkstrough;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L4613-L4651
                data = data(~any(isnan(data),2),:); % remove NaN values
                data = sortrows(data);  % sort first column
                data=findduplicate(data); % remove duplicate number
                data(any(isinf(data),2),:) = []; % remove empty
                %
                if pkstrough == 1
                    [datapks,~] = getpks(data);
                    plot_filter_s ='max';
                else
                    data(:,2) = -1*data(:,2);
                    [datapks,~] = getpks(data);
                    plot_filter_s ='min';
                end

                [nrow, ~] = size(datapks);
                
                % age model
                datapksperiod = 1:nrow;
                datapksperiod = datapksperiod*period;
                datapksperiod = datapksperiod';
                agemodel = [datapks(:,1),datapksperiod];
                
                % sed. rate 
                sedrate = zeros(nrow+2,2);
                sedrate(1,1) = data(1,1);
                sedrate(2:end-1,1) = datapks(:,1);
                sedrate(end,1) = data(end,1);
                sedrate0 = diff(agemodel(:,1))./diff(agemodel(:,2));
                sedrate(2:end-2,2) = sedrate0;
                sedrate(1,2) = sedrate(2,2);
                sedrate(end-1,2) = sedrate(end-2,2);
                sedrate(end,2) = sedrate(end-2,2);
                % full age model
                agemodelfull = zeros(nrow+2,2);
                agemodelfull(2:end-1,:) = agemodel;
                agemodelfull(1,1) = data(1,1);
                agemodelfull(1,2) = datapksperiod(1) - (agemodelfull(2,1)-agemodelfull(1,1)) * sedrate(1,2);
                agemodelfull(end,1) = data(end,1);
                agemodelfull(end,2) = datapksperiod(end) + (agemodelfull(end,1)-agemodelfull(end-1,1)) * sedrate(end,2);
%% End copied source
r = struct();
r.agemodel = agemodel;
r.agemodelfull = agemodelfull;
r.sedrate = sedrate;
r.period = period;
r.plot_filter_s = plot_filter_s;
end
