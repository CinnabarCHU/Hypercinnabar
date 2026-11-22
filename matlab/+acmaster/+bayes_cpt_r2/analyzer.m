function [retval,id] = analyzer(params,id)
% bayes_cpt_r2.analyzer parameters: data k_max d_min k_0 v_0 sig_0 num_samp.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bayes_changepoint/bayes_cpt_r2.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('bayes_cpt_r2-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
k_max = p.k_max;
d_min = p.d_min;
k_0 = p.k_0;
v_0 = p.v_0;
sig_0 = p.sig_0;
num_samp = p.num_samp;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/bayes_changepoint/bayes_cpt_r2.m:L75-L265

% Outline of the Bayesian Change Point algorithm:
% 1) Load the Data  
% 2) Define the Parameter Values
% 3) Calculate the Probability Density of the Data for Each Sub-Interval
% 4) Forward Recursion [Dynamic Programming]
% 5) Stochastic Backtrace via Bayes Rule
%       a) Sample a Number of Change Points
%       b) Sample the Location of the Change Points
%       c) Sample the Regression Parameters Between Adjacent Change Points
% 6) Plot the Results
%
% Description of Parameters, input, and output can be found in accompanying 
% ReadMe file
%

%% ************(1)Load the Data*****************************

Y=data(:,2);    % Data set / time series (didn't work well, still doesn't)
x=data(:,1);    % Time points

%% *************(2)Define the Parameter Values**************

N=length(Y);    % Number of data points
% k_max=10;        % Maximum number of change points
% d_min=1;       % Minimum distance between adjacent change points 
% k_0=0.0001;           % Hyperparameter for the prior on the regression coefficients
% v_0=0.01; 
% sig_0=0.001;  % Hyperparameter for scaled inverse chi-square prior on the variance

X = [zeros(N,1)+1 (1:N)'];  % Build the regression model - in this case, a linear model
                            % Column 1 represents the constant term
                            % Column 2 represents the linear trend

[~, m] =size(X);             % r = total # data points (N), m = # regressors
beta0= zeros(m,1);          % Mean of multivariate normal prior on regression coefficients
%num_samp=500;               % Number of sampled solutions

%% ******(3)Calculate the Probability Density of Data for Each Sub-Interval*********

Py=zeros(N,N)-Inf;      % Matrix containing the probability of each substring of the data
I=eye(m);               % cxc identity matrix

for i=1:N
    for j=i+d_min-1:N
        
        %Calculate beta_hat
        XTy=X(i:j,:)'*Y(i:j); 
        J=k_0*I+X(i:j,:)'*X(i:j,:); 
        beta_hat=J\(k_0*beta0+XTy); %inv(J)*(k_0*beta0+XTy)
        
        %Calculate v_n and s_n
        a=j-i+1;    % 'a' is the number of data points.... not the distance between them, 
                    % which becomes relevant if data points are not equally spaced
        v_n=v_0+a;  % a is the number of data points in the segment, see above for definition
        
        s_n = v_0*sig_0 + k_0*(beta0-beta_hat)'*(beta0-beta_hat) + (Y(i:j,:)-X(i:j,:)*beta_hat)'*(Y(i:j,:)-X(i:j,:)*beta_hat);
        
        % Calculate the Probability Density of the Data - Equation (2) - stored in log form 
        Py(i,j) = v_0*log(sig_0*v_0/2)/2 + gammaln(v_n/2) +m*log(k_0)/2  ...
            - log(gamma(v_0/2)) - v_n*log(s_n/2)/2 - a*log(2*pi)/2 - log(det(J))/2 ;
     end
end

R_2_all = zeros(k_max,2);

for ii = 1:k_max
%****************(4) Build Partition Function *************************
P = partition_fn(Py, k_max, N);
        
%****************(5) Stochastic Backtrace via Bayes Rule****************

k= P(:,N);
for i=1:k_max                   % Equation (6)
    if(N-(i+1)*d_min+i >= i)    % If a plausible solution exists...
        k(i) = k(i) + log(0.5) - log(k_max) - log(nCk(N-(i+1)*d_min+i,i));
                                                % Above term is N_k
    end
end
k=[Py(1,N)+ log(0.5); k];       % Zero change points

total_k = log(sum(exp(k))); % Adds logarithms and puts answer in log form - Equation (5) 
%total_k=logsumlog(k);      % A slower, but potentially more precise version of above calculation
k(:)=exp(k(:)-total_k);     % Normalize the vector - Equation (7)

% Variables used in sampling procedure:
samp_holder=zeros(num_samp,k_max);  % Contains each of the num_samp change point solutions
chgpt_loc=zeros(1,N);               % The number of times a change point is identified at each data point
BETA = zeros(m,N);                  % Holds the regression coefficients

for i=1:num_samp
    %******** (5a) Sample a Number of Change Points ***********************
    num_chgpts = pick_k1(k)-1;  % Since we allow for 0 changepoints, function returns the index of the 'k' vector, 
                                % which is offset from the number of change points by 1 
    if(num_chgpts>0)
        
        %******** (5b) Sample the Location of the Change Points ***********
        back=N;
        for kk=num_chgpts:-1:2      % Start at the end of the time series and work backwards
            temp=zeros(1,back-1);
            for v=1:back-1
                temp(v)= P(kk-1,v)+Py(v+1,back);  % Build the vector to sample from
            end
            total = log(sum(exp(temp)));
            %total=logsumlog(temp);      % Slower, but potentially more precise version of above calculation    
            temp(:)=exp(temp(:)-total);  % Normalize the vector
            changepoint=pick_k1(temp);   % Sample the location of the change point
            chgpt_loc(changepoint)= chgpt_loc(changepoint) +1; % Keep track of change point locations
            samp_holder(i,kk)=changepoint;  % Keep track of individual change point solutions
            
            %******** (5c) Sample the Regression Parameters ***********
            % Regression Coefficients (Beta)
            XTy=X(changepoint+1:back,:)'*Y(changepoint+1:back); 
            J=k_0*I+X(changepoint+1:back,:)'*X(changepoint+1:back,:); 
            beta_hat=J\(k_0*beta0+XTy);     %inv(J)*(k_0*beta0+XTy)
            
            for j=1:m
               BETA(j,changepoint+1:back) = BETA(j,changepoint+1:back) +beta_hat(j)*ones(1,back-changepoint);  
            end
            
            back=changepoint;   % Now work with the next segment
        end
        
        % The final changepoint
        %******** (5b) Sample the Location of the Change Points ***********
        kk=1;
        temp=zeros(1,back-1);
        for v=1:back-1
            temp(v)= Py(1,v)+Py(v+1,back); %Build the vector to sample from
        end
        total = log(sum(exp(temp)));
        %total=logsumlog(temp);      % Slower, but potentially more precise version of above calculation    
        temp(:)=exp(temp(:)-total); % Normalize the vector
        changepoint=pick_k1(temp);  % Sample the location of the change point
        chgpt_loc(changepoint)= chgpt_loc(changepoint) +1; % Keep track of change point locations
        samp_holder(i,kk)=changepoint;  % Keep track of individual change point solutions
            
        %******** (5c) Sample the Regression Parameters ***********
        % Regression Coefficients (Beta)
        XTy=X(changepoint+1:back,:)'*Y(changepoint+1:back); 
        J=k_0*I+X(changepoint+1:back,:)'*X(changepoint+1:back,:); 
        beta_hat=J\(k_0*beta0+XTy);     %inv(J)*(k_0*beta0+XTy)
        
        for j=1:m
               BETA(j,changepoint+1:back) = BETA(j,changepoint+1:back) +beta_hat(j)*ones(1,back-changepoint);  
        end
        
        %The final sub-interval
        XTy=X(1:changepoint,:)'*Y(1:changepoint); 
        J=k_0*I+X(1:changepoint,:)'*X(1:changepoint,:); 
        beta_hat=J\(k_0*beta0+XTy);     %inv(J)*(k_0*beta0+XTy)
        
        for j=1:m
               BETA(j,1:changepoint) = BETA(j,1:changepoint) +beta_hat(j)*ones(1,changepoint);  
        end
        
    else    % 0 change points, so a single homogeneous segment
        XTy=X'*Y; 
        J=k_0*I+X'*X; 
        
        %******** (5c) Sample the Regression Parameters ***********
        % Regression Coefficients (Beta)
        beta_hat=J\(k_0*beta0+XTy);     %inv(J)*(k_0*beta0+XTy)
        for j=1:m
               BETA(j,:) = BETA(j,:) +beta_hat(j)*ones(1,N);  
        end
    end
end

BETA=BETA/num_samp;             % Average regression coefficient at each data point.
chgpt_loc=chgpt_loc/num_samp;   % Posterior probability of a change point

%**********(6) Plot the Results ********************************
% Adapt as Necessary

model=zeros(1,N);
for i=1:N
    model(i)=X(i,:)*BETA(:,i);
end

% Calculate R^2 value:
r=0; rr=0;
for i=1:N
    r = r+ Y(i)^2;
    rr= rr+ (Y(i)-model(i))^2;
end

R_2 = 1-rr/r;

R_2_all(ii,:)=[ii,R_2];
end
%% End copied source
r = struct();
r.R_2_all = R_2_all;
end
