function [retval, id] = plotter(params, id)
% OneSampleT.plotter parameters: miu option_cal dof t_critical ci_left t.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/univariate/Unittest.m#L231
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('OneSampleT-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
miu = p.miu;
option_cal = p.option_cal;
dof = p.dof;
t_critical = p.t_critical;
ci_left = p.ci_left;
t = p.t;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/univariate/Unittest.m:L231-L258
        fig1 = findobj('Type', 'figure', 'Name', 'Acycle: t test plot');
        % If no such figure exists, create a new one
        if isempty(fig1)
            fig1 = figure('Name', 'Acycle: t test plot','NumberTitle', 'off');
        else
            figure(fig1)
        end
        % PDF
        if miu > 5
            xlim1 = 1.2*miu;
        else
            xlim1 = 5;
        end
        x = -1*xlim1 : .1 : xlim1;
        y = tpdf(x,dof);
        % plot
        plot(x,y,'k-')
        hold on
        xline(t_critical,'k--')
        if option_cal == 1 
            xline(ci_left,'k--')
        end
        xline(t,'r-')
        xlabel('Observation')
        ylabel('Probability Density')
        legend({['dof = ',num2str(dof)],['t = ',num2str(t_critical),' @ 95% CI'],['t = ',num2str(t),'@ μ = ',num2str(miu)]})
        title('Testing the mean: probability of a value ')
        hold off
%% End copied source
r=[];
end
