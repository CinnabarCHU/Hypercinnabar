function [retval,id] = plotter(params,id)
% ecocotrack.plotter parameters: result out_depth sr1 sr2 srstep.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ecocotrack.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ecocotrack-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
out_depth = p.out_depth;
sr1 = p.sr1;
sr2 = p.sr2;
srstep = p.srstep;
srn_best=p.result.srn_best;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/corrcoef/ecocotrack.m:L97-L104
figure; 
plot(sr1+srstep*(srn_best(1,:)-1),out_depth,'o')
xlim([sr1 sr2])
ylim([min(out_depth) max(out_depth)])
xlabel('Sedimentation rate (cm/kyr)')
ylabel('Depth (m)')
title('Tracked highest ecoco*SL*#orbits value')
set(gca,'Ydir','reverse')
%% End copied source
r=[];
end
