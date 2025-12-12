.data
getX:
	.asciiz "Enter the multiplicand: "
getY:
	.asciiz "Enter the multiplier: "
str1:
	.asciiz " * "
str2:
	.asciiz " = "

# Inputs:  $a0 : multiplicand, $a1 : multiplier
# Outputs:  $v0 : product
.text
main:
	# get X
	li $v0, 4
	la $a0, getX
	syscall
	
	li $v0, 5
	syscall                           # prompt
	
	move $a2, $v0                     # placeholder
	# print newline
	li $v0, 11
	li $a0, 10
	syscall
	
	# get Y
	li $v0, 4
	la $a0, getY
	syscall
	
	li $v0, 5
	syscall                           # prompt
	
	move $a1, $v0
	# print newline
	li $v0, 11
	li $a0, 10
	syscall
	
	move $a0, $a2                     # $a2 was a placeholder
	
	# print "X * Y = "
	li $v0, 1
	syscall
	li $v0, 4
	la $a0, str1
	syscall
	move $a0, $a1
	li $v0, 1
	syscall
	li $v0, 4
	la $a0, str2
	syscall
	
	move $a0, $a2                     # $a2 was a placeholder

	jal recursiveMultiply
	
	# print $v0
	move $a0, $v0
	li $v0, 1
	syscall	
	# exit
	li $v0, 10
	syscall
			
recursiveMultiply:
	# allocate space on the stack
	subu $sp, $sp, 8
	sw $ra, ($sp)
	sw $s0, 4($sp)
	
	# base case
	li $v0, 0
	beq $a0, 0, factorialDone
	
	# recursive
	move $s0, $a0
	subu $a0, $a0, 1
	jal recursiveMultiply
	
	add $v0, $v0, $a1
	
factorialDone:
	lw $ra, ($sp)
	lw $s0, 4($sp)
	addu $sp, $sp, 8
	jr $ra
