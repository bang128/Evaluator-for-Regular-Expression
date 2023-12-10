# Evaluator-for-Regular-Expression
## Objective
This project is written in python. It is to evaluate expressions (include numbers and operators) based on the AST generated by parser, and then return a single numeric output. The key idea here is using a stack. Particularly, in main function, if the AST is able to be generated, the program creates an empty stack, then call the function evaluator(stack, tree) to evaluate the AST.
## Instruction
To run this program, the user needs to have input file (test_input) and output file (test_output), then use the command line python evaluator.py test_input test_output. 
