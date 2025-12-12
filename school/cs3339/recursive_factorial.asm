.text
main:
	li $a0, 8
	jal factorial
	
	move $a0, $v0
	li $v0, 1
	syscall
	
	li $v0, 10
	syscall
	
factorial:
	li $v0, 1
	# base case
	beqz $a0, factorial_exit
	addi $a0, $a0, -1
	addi $sp, $sp, -4
	sw $ra, ($sp)
	# recursive
	lw $ra, ($sp)
	addi $sp, $sp, 4
	addi $a0, $a0, 1
	mul $v0, $v0, $a0
factorial_exit:
	jr $ra