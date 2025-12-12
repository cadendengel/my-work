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
	li $v0, 0                         # prep $v0 for recursion
				
	slt $t1, $a1, $a0                 # checks if $a0 > $a1
	bne $t1, $zero, swapRegisters     # if $s0 > $s1, goto swapRegisters

# now, $a0 <= $a1 in all cases
#
# we want $a0 to be less because 
# it will be the amount of additions
# the program has to do
# 
# in other words...
# $a0 is the counter
recursive:
	beqz $a0, exit
	add $v0, $v0, $a1
	subi $a0, $a0, 1
	b recursive

# for increasing average performance
swapRegisters:
	move $t1, $a0
	move $a0, $a1
	move $a1, $t1
	b recursive

# exit
exit:
	#print $v0
	move $a0, $v0
	li $v0, 1
	syscall	
	
	#exit
	li $v0, 10
	syscall