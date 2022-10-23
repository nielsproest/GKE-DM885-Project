% Balanced Incomplete Block Design model
/*
Problem:
A way of defining a BIBD is in terms of its incidence matrix: 
A v by b binary matrix with exactly r ones per row, k ones per column, and with a scalar product of λ between any pair of distinct rows. 
A BIBD is therefore specified by its parameters (v,b,r,k,λ). Example: (7,7,3,3,1)
*/ 

% Hardtyped variables (mimic example), move to datafile 
int: v = 7;
int: b = 7;
int: r = 3;
int: k = 3;
int: lam = 1;

% Set up the matrix
set of int: cell = 0..1;
set of int: HEIGHT = 1..v;
set of int: WIDTH = 1..b;
array[HEIGHT,WIDTH] of var cell: t;

% Contraints
constraint forall(j in HEIGHT)( sum(t[j,1..v]) = r ); % r restraint
constraint forall(i in WIDTH)( sum(t[1..v,i]) = k ); % k restraint
constraint forall(x, y in HEIGHT where x != y)((sum (i in 1..v) (t[x,i]*t[y,i])) = lam); % scalar product restraint

% Solve
solve satisfy;

% Output
output [
    show_int(2,t[j,i]) ++
    if i == 7 then "\n" else " " endif | j in HEIGHT, i in WIDTH
];