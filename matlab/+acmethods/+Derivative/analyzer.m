function [retval, id] = analyzer(params, id)
% Derivative.analyzer parameters: data derivative_n.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L2691
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Derivative-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
derivative_n = p.derivative_n;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2691-L2703
                int_gt_0 = @(n) (rem(n,1) == 0) & (n > 0);
                math_derivative = int_gt_0(derivative_n);

                if math_derivative == 1
                    data = data(~any(isnan(data),2),:); % remove NaN values
                    data = sortrows(data);
                    time  = data(:,1);
                    value = data(:,2);
                    for i=1:derivative_n
                        value= diff(value)./diff(time);
                        time = time(1:length(time)-1,1);
                    end
                    data1 = [time,value];
%% End copied source
else, error('Acycle:Derivative:Order','Expected a positive integer derivative order.'); end
r = struct();
r.data1 = data1;
end
