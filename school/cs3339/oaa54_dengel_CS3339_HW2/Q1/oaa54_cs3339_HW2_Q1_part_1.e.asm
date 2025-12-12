.data
	D: .space 400
	str1: .asciiz "Enter a: "
	str2: .asciiz "Enter b: "
.text
main:
	# $s0 = a
	# $s1 = b
	# $t0 = i
	# $t1 = j
	# $s2 = D[]
	
	# $t2 = index of array
	# $t3 = value to set D[$t2] to
	
	# for (i = 0; i < a; i++)
	# 	for (j = 0; j < b; j++)
	# 		D[j + b * j] = i + j;
	
	# link D to $s2
	la $s2, D
	
	# print str1
	la $a0, str1
    	li $v0, 4
    	syscall
    	
    	# get a
    	li $v0, 5
	syscall
	move $s0, $v0
	
	# print str2
	la $a0, str2
    	li $v0, 4
    	syscall
    	
    	# get b
    	li $v0, 5
	syscall
	move $s1, $v0

	# start at i = 0
	li $t0, 0
loop1:
	# start at j = 0
	li $t1, 0
loop2:
	# D[j + b * j] = i + j;
	# getting the index --> address
	# $t2 = b * i
	mul $t2, $t0, $s1
	# $t2(b * i) += j
	addu $t2, $t2, $t1
	sll $t2, $t2, 2
	# getting the address
	addu $t2, $t2, $s2
	# value to input into the array
	addu $t3, $t0, $t1
	# inputting to the array
	sw $t3, ($t2)
	
	# loop2 content
	addiu $t1, $t1, 1
	blt $t1, $s1, loop2
	
	# loop1 content
	addiu $t0, $t0, 1
	ble $t0, $s0, loop1

	
############################
# printing all values of D #
############################

	# j = a * b
	mul $t1, $s0, $s1
	# i = 0
	li $t0, 0
loop3:
	# printing the value from array
	li $v0, 1
	lw $a0, ($s2)
	syscall
	
	# print newline
	li $v0, 11
	li $a0, 10
	syscall
	
	# increment array and counter
	addiu $s2, $s2, 4
	addiu $t0, $t0, 1
	
	blt $t0, $t1, loop3
