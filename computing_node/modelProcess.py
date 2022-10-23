from builtins import print
from minizinc import Instance, Model, Solver
import sys

def main() -> int:

    # Read the sys.argv (Could have been added directly but this makes it easier to read)
    modelArg = sys.argv[1]
    solverArg = sys.argv[2]

    model = Model(modelArg) # Takes the path to the model
    solver = Solver.lookup(solverArg) # Takes a string matching the name of a solver

    # If a datafile was provided
    if (len(sys.argv) == 4):
        dataArg = sys.argv[3]
        model.add_file(dataArg) # Add datafile

    instance = Instance(solver, model) # Creates an instance of the solver + model
    result = instance.solve() # Attempts to solve the model

    print(result.solution)
    print(result.statistics)

    return 0

if __name__ == '__main__':
    sys.exit(main())  