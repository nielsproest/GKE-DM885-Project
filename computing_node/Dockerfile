# Gets prepped image
FROM blackdux/minizinc_computing_container:latest

#Grab some args
ARG modelfile

# Copy python script and model (Prolly needs to be changed)
COPY ${modelfile} ./scripts

# Mabye it needs to run minizinc aswell? 
# Then it needs to take an argument (a solver) and run the python script to run minzinc
#CMD ["python3","modelProcess.py","scripts/" + modelFile, solver]