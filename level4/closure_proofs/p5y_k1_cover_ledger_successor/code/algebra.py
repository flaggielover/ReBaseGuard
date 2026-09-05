"""Exact rational reference algebra for specification tests; NOT a scientific kernel."""
from dataclasses import dataclass
from fractions import Fraction as F

M_VALUES=(1,2,3,5)
TOP_BUDGETS={'B_cover':F(1,20), 'B_candidate':F(1,25), 'B_kernel':F(1,25),
             'B_other':F(1,25), 'B_rounding':F(1,100), 'B_interval':F(1,100)}
CLAIMANTS={
    'F_equation_certificate_value':'B_candidate',
    'source_dependency_value':'B_kernel',
    'finite_kernel_chain_value':'B_kernel',
    'value_export_rounding_not_in_certificate':'B_rounding',
    'value_assembly_arithmetic_not_in_certificate':'B_interval',
    'nominal_drift_variation':'B_cover',
    'dF_equation_certificate':'B_cover',
    'Kprime_F_dependency':'B_cover',
    'derivative_source_dependency':'B_cover',
    'finite_derivative_chain':'B_cover',
    'derivative_arithmetic':'B_cover',
    'curvature_envelope':'B_cover',
    'cover_arithmetic':'B_cover',
}

@dataclass(frozen=True)
class Interval:
    lo:F
    hi:F
    def __post_init__(self):
        object.__setattr__(self,'lo',F(self.lo));object.__setattr__(self,'hi',F(self.hi))
        if self.lo>self.hi:raise ValueError('reversed interval')
    def __add__(self,other):
        if not isinstance(other,Interval):other=Interval(other,other)
        return Interval(self.lo+other.lo,self.hi+other.hi)
    __radd__=__add__
    def __mul__(self,other):
        if not isinstance(other,Interval):other=Interval(other,other)
        v=[self.lo*other.lo,self.lo*other.hi,self.hi*other.lo,self.hi*other.hi]
        return Interval(min(v),max(v))
    __rmul__=__mul__
    @property
    def mag(self):return max(abs(self.lo),abs(self.hi))
    @property
    def radius(self):return (self.hi-self.lo)/2


def terms(m):
    if m not in M_VALUES:raise ValueError('outside frozen m scope')
    out=[('F',r,0,F(1,m)) for r in range(m)]
    out += [('W',r,t-r-1,F(1,t)-F(1,m)) for t in range(1,m) for r in range(t)]
    return out


def assemble(m, F_intervals, W_intervals):
    """Same positive exact coefficients for R, R', R''. Supply each derivative order separately."""
    out=Interval(0,0)
    for kind,r,j,c in terms(m):
        out=out+(F_intervals[r] if kind=='F' else W_intervals[r,j])*c
    return out


def resolvent_errors(C,delta_F,epsilon_S,k1,delta_D,epsilon_Sprime):
    args=tuple(map(F,(C,delta_F,epsilon_S,k1,delta_D,epsilon_Sprime)))
    if min(args)<0:raise ValueError('negative error input')
    C,delta_F,epsilon_S,k1,delta_D,epsilon_Sprime=args
    epsilon_F=C*(delta_F+epsilon_S)
    epsilon_D=C*(delta_D+k1*epsilon_F+epsilon_Sprime)
    return epsilon_F,epsilon_D


def power_error_step(k0,k1,k2,errors,local_errors):
    """Leibniz error recurrence for W_next=K W, orders 0,1,2.

    local_errors bound the TRUE operator applied to the chosen previous
    candidates, including any numerical operator approximation error.
    """
    e0,e1,e2=map(F,errors); l0,l1,l2=map(F,local_errors)
    return (F(k0)*e0+l0,F(k0)*e1+F(k1)*e0+l1,
            F(k0)*e2+2*F(k1)*e1+F(k2)*e0+l2)


def cover(R_interval,D_interval,rho,M_R2,*,separate_derivative_charge=None):
    """STYLE_1 only. No separate rho*epsilon_D permitted."""
    if separate_derivative_charge is not None:
        raise ValueError('derivative uncertainty is already inside D_interval')
    rho,M_R2=F(rho),F(M_R2)
    if rho<0 or M_R2<0:raise ValueError('negative radius/curvature')
    width=rho*D_interval.mag+rho*rho*M_R2/2
    return R_interval+Interval(-width,width),width


def shard(N,k,S):
    if not (N>=0 and S>0 and 0<=k<S):raise ValueError('invalid shard')
    return N*k//S,N*(k+1)//S


def work_ids(cells):
    """Each cell owns all scientific dependencies, named separately for resumption."""
    ids=[]
    objects=([f'h_{j}' for j in range(1,5)]+[f'S_{r}' for r in range(5)]
             +[f'F_{r}' for r in range(5)]+[f'dF_{r}' for r in range(5)])
    for c in cells:
        prefix=(c['detector'],c['index'])
        ids += [(*prefix,'object',obj) for obj in objects]
        # Complete source derivative + finite-power bundle, across all m.
        ids.append((*prefix,'dependency_bundle','orders_0_1'))
        ids += [(*prefix,'curvature',str(m)) for m in M_VALUES]
        ids += [(*prefix,'assembly',str(m)) for m in M_VALUES]
    ids += [(det,-1,'far_field','all_m') for det in ('CUSUM','SR')]
    return ids


def unit_dependencies(cells):
    """Frozen certificate dependency graph, not a production scheduler.

    m=5 owns the shared uniform-cell curvature inputs; other m consume hashes.
    Identity order need not be execution order; no unit runs before dependencies.
    """
    graph={u:set() for u in work_ids(cells)}
    for cell in cells:
        prefix=(cell['detector'],cell['index'])
        obj=lambda name:(*prefix,'object',name)
        bundle=(*prefix,'dependency_bundle','orders_0_1')
        for j in range(2,5):graph[obj(f'h_{j}')].add(obj(f'h_{j-1}'))
        for r in range(1,5):graph[obj(f'S_{r}')].add(obj(f'h_{r}'))
        graph[bundle].update(obj(f'h_{j}') for j in range(1,5))
        graph[bundle].update(obj(f'S_{r}') for r in range(5))
        for r in range(5):
            graph[obj(f'F_{r}')].add(obj(f'S_{r}'))
            graph[obj(f'dF_{r}')].update((obj(f'F_{r}'),bundle))
        owner=(*prefix,'curvature','5')
        graph[owner].update(u for u in graph if u[:2]==prefix and u[2]=='object')
        graph[owner].add(bundle)
        for m in M_VALUES:
            cur=(*prefix,'curvature',str(m))
            if m!=5:graph[cur].add(owner)
            ass=(*prefix,'assembly',str(m))
            graph[ass].update((bundle,cur))
            for r in range(m):graph[ass].update((obj(f'F_{r}'),obj(f'dF_{r}')))
    return graph


def require_production():
    raise RuntimeError('PRODUCTION_DISABLED: governance-only successor; missing certified kernels and cost qualification')
