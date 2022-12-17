int: amount = 78;
array[1..4] of int: denoms = [25, 10, 5, 1];

array[1..4] of var 0..100: counts;

% ------------------------------------------

constraint sum(i in 1..4) ( counts[i] * denoms[i] ) = amount;

var int: coins = sum(counts);
solve minimize coins;

output [
  "coins = ", show(coins), ";\n",
  "denoms = ", show(denoms), ";\n",
  "counts = ", show(counts), ";\n"
];
