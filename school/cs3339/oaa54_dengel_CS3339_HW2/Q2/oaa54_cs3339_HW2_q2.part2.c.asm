.data
	prompt: .asciiz "Enter a number: "
	answer1: .asciiz "Fib("
	answer2: .asciiz ")= "

.text
main:
	# prompt user
	la $a0, prompt   
	li $v0, 4
	syscall

	# get user input
	li $v0, 5
	syscall

	# store user input
	move $t0, $v0

	# prep for fib()
	move $a0, $t0
	move $v0, $t0
	# call fib()
	jal fib
	# for printing
	move $t1, $v0

	# print answer
	la $a0, answer1
	li $v0, 4
	syscall

	move $a0, $t0
	li $v0,1
	syscall

	la $a0, answer2
	li $v0, 4
	syscall

	move $a0, $t1
	li $v0, 1
	syscall

	li $a0, 10
	li $v0, 11
	syscall

	# exit
	li $v0, 10
	syscall
#######################################
# calculates the n-th fibonacci number#
#######################################
fib:
	# if (n == 0) return 0;
	beqz $a0, returnZero
	#if (n == 1) return 1;
	beq $a0, 1, returnOne

	# fib(n-1)

	# push ra to stack
	addi $sp, $sp, -4
	sw $ra, ($sp)

	# n - 1
	sub $a0, $a0, 1
	jal fib

	# return to n for printing later
	add $a0, $a0, 1

	# get ra from stack
	lw $ra, ($sp)
	add $sp, $sp, 4

	# push return value to stack
	addi $sp, $sp, -4
	sw $v0, ($sp)

	# fib(n - 2)

	# push ra to stack
	addi $sp, $sp, -4
	sw $ra, ($sp)

	# n - 2
	sub $a0, $a0, 2 
	jal fib
	add $a0,$a0,2

	# get ra from stack
	lw $ra, ($sp)
	add $sp, $sp, 4

	# get return value from stack
	lw $t2, 0($sp)
	add $sp,$sp,4

	# f(n - 2) + fib(n - 1)
	add $v0, $v0, $t2
	jr $ra

returnZero:
	li $v0, 0
	jr $ra
returnOne:
	li $v0, 1
	jr $ra