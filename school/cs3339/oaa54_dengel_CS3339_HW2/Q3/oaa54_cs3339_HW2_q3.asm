.data
	string: .asciiz "loop"
.text
main:
la $a0, string
# character to look for...'o' = 111
li $a1, 111

	
loop:
	lbu $t1, ($a0)
	# if newline
	beqz $t1, exit
	# if current element is not char, skip incrementing
	bne $t1, $a1, skip
	# increment counter
	addiu $t2, $t2, 1
skip:
	# next char in string
	addi $a0, $a0, 1
	# loop
	j loop
exit:
	# print answer
	li $v0, 1
	move $a0, $t2
	syscall
