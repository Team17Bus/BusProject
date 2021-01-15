function [U,beta,num_it]=nerfcm(R,c, m, epsilon)
% MATLAB (Version 4.1) Source Code (Routine nerfcm was written by Richard J.
% Hathaway on June 26, 1992.  Modified on 6/15/94.)  The fuzzification constant
% m = 2, and the stopping criterion for successive partitions is epsilon =.0001. 
%
% Purpose:The function nerfcm attempts to find a useful clustering of the
%		objects represented by the dissimilarity data in R using the initial
% 		partition	in U0.
%
%	Usage:	[U,beta,num_it]=nerfcm(R,c,m,e)
%
%	where:	c  = number of clusters
%           m  = fuzzifier
%			R  = on entry, the dissimilarity data matrix of size n x n
%           e = use 0.0001
%			U  = on exit, the final partition matrix of size c x n
%			beta = on exit, the simulated off diagonal addition to R
%			num_it = on exit, the number of iterations done
%


   	n=size(R,1);
    U0=zeros(c,n);
    %[mmm,ind]=min(R);
    psize=ceil(n/c);
    temp=1;
    for i=1:n
        ind(i)=temp;
        if mod(i,psize)==0
            temp=temp+1;
        end
    end
    U0=zeros(c,n);
    for i=1:n
        U0(ind(i),i)=1;
    end
    %U0=U0./(ones(c,1)*sum(U0));
    
    if min(min(U0)) < 0 | max(max(U0)) > 1 | any(abs(sum(U0) - 1) > .001),
		error('U0 is not properly initialized.')
    elseif min(min(R)) < 0 | any(any(abs(R - R') > 0)) | max(diag(R)) > 0,
		%error('R is not properly initialized.')
	elseif size(R) ~= [n,n],
		error('Dimensions of U0 and R are inconsistent.')
   	end;
%
%     %make R Euclidean
%      P=eye(n)-ones(n)/n;
%      work=eig(P*R*P);
%      max_eig=max(real(work));
%      if max_eig>0
%          R=R+max_eig*(ones(n)-eye(n));
%      end
%	Initialize variables:
%
    %epsilon=.0001;
   	d_adjustment=zeros(c,n); num_it=0; max_it=100; U=U0;
	beta=0.0001;  min_d=1.0e-10; step_size=epsilon;%m=5;
% 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%	Begin the main loop:
%
   while  num_it < max_it & step_size >= epsilon,
		num_it = num_it + 1;
		U0 = U;
        %
        %%%% Get new V prototypes:  
        %
        V=U0.^m;      
		work = sum(V');
		for i=1:c
            V(i,:) = V(i,:) / work(i); 
        end
        %
        %%%%	Get new (quasi-squared-distance values) d:
        %
        %	First, get new initial values for d:
		for i=1:c, 
            d(i,:)=R*V(i,:)'-V(i,:)*R*V(i,:)'/2;
		end
        %	Second, adjust any negative d values to be at least as big as min_d by
        %	adjusting beta:
		j = find(d < 0);
		if ~isempty(j)
			for i=1:c,
				work = (V(i,:) * V(i,:)' +1) / 2;
				d_adjustment(i,:) = work - V(i,:); 
			end
			work = (min_d - d(j)) ./ d_adjustment(j);
			beta_adjustment = max(work);
			beta = beta + beta_adjustment;
			d = d + beta_adjustment * d_adjustment;
			R = R + beta_adjustment * (ones(size(R)) - eye(size(R)));
		end
        %	Third, adjust all d values to be at least as big as min_d:
        d(d<min_d)=min_d;

        %
        %%%% Get new partition matrix U:
        %
        d=d.^(1/(m-1));
		work = 1 ./ d;
		work = sum(work);
        U=1./d;
		for i=1:c, U(i,:) = U(i,:) ./ work; end

        %
        %%%% Calculate step_size and return to top of loop:
        %
		step_size=max(max(abs(U-U0)));
        %
        %	End the main loop:
        %
   	end
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
