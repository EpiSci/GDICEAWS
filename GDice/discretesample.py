import numpy as np

def discretesample(p,n):
# Samples from a discrete distribution
#
#   x = discretesample(p, n)
#       independently draws n samples (with replacement) from the 
#       distribution specified by p, where p is a probability array 
#       whose elements sum to 1.
#
#       Suppose the sample space comprises K distinct objects, then
#       p should be an array with K elements. In the output, x(i) = k
#       means that the k-th object is drawn at the i-th trial.
#       
#   Remarks
#   -------
#       - This function is mainly for efficient sampling in non-uniform 
#         distribution, which can be either parametric or non-parametric.         
#
#       - The function is implemented based on histc, which has been 
#         highly optimized by mathworks. The basic idea is to divide
#         the range [0, 1] into K bins, with the length of each bin 
#         proportional to the probability mass. And then, n values are
#         drawn from a uniform distribution in [0, 1], and the bins that
#         these values fall into are picked as results.
#
#       - This function can also be employed for continuous distribution
#         in 1D/2D dimensional space, where the distribution can be
#         effectively discretized.
#
#       - This function can also be useful for sampling from distributions
#         which can be considered as weighted sum of "modes". 
#         In this type of applications, you can first randomly choose 
#         a mode, and then sample from that mode. The process of choosing
#         a mode according to the weights can be accomplished with this
#         function.
#
#   Examples
#   --------
#       # sample from a uniform distribution for K objects.
#       p = ones(1, K) / K;
#       x = discretesample(p, n);
#
#       # sample from a non-uniform distribution given by user
#       x = discretesample([0.6 0.3 0.1], n);
#
#       # sample from a parametric discrete distribution with
#       # probability mass function given by f.
#       p = f(1:K);
#       x = discretesample(p, n);
#

#   Created by Dahua Lin, On Oct 27, 2008
#   Converted to Python by Garrett Fosdick, On Sept 25, 2019
#------------------------------------------------------------------------------------#
    ## parse and verify input arguments
    assert (p.dtype == np.dtype('Float64')) , "p should be an array with floating-point value type."
    assert ((type(n) is int) and (n >= 0)) , "n should be a nonnegative integer scalar."
    
    ## main
    # process p if necessary
    
    K = p.size
    if p.shape != (1,K):
        p = np.reshape(p,(1,K))
        
    # construct the bins
    
    edges = np.append(0,np.cumsum(p))
    s = edges[-1]
    if np.abs(s-1) > np.finfo(np.float64).eps:
        edges = edges * (1/s)
        
    # draw bins
    
    rv = np.random.rand(1,n)
    c = np.histogram(rv,edges)[0]
    
    # extract samples
    xv = np.argwhere(c>0).flatten()
    
    if xv.size == n: # each value is sampled at most once
        x = xv
    else:
        xc = c[xv]
        d = np.zeros(n)
        dv = np.append(xv[0],np.diff(xv))
        dp = np.append(0, np.cumsum(xc[0:-1]))
        d[dp] = dv
        x = np.cumsum(d)
        
    # randomly permute the sample's order
    x = x[np.random.permutation(n)]
    
    return x.astype(int)
