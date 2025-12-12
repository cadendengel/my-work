.data

chars:    .ascii "ABCDEFGHIJKLMNOPQRSTUVWXYZ .,!-'"
msg1:     .word 0x93EA9646, 0xCDE50442, 0x34D29306, 0xD1F33720
          .word 0x56033D01, 0x394D963B, 0xDE7BEFA4  

.text

main:
	la $t0, msg1
	add $t1, $zero, $zero
	li $t3, 28                # 28 bytes
	li $s0, 0                 # decimal value of binary number
	li $s1, 0                 # bit counter: 0 - 5
	li $s2, 0                 # byte counter: 0 - 8
	li $s3, 4                 # current power

# main loop for bytes, exits when the end is reached ($t3)
loop:
	lb $s7, ($t0)
	beqz $t3, exit
	sub $t3, $t3, 1
	addi $t2, $zero, 1
	sll $t2, $t2, 7

# convert the 5-bit binary number to decimal number and save into $s0
checkBit:
	and $t4, $t2, $s7
	# if bit is 0, skip
	beqz $t4, skip1
	# else the bit is 1, so add the value (based on position) to $s0
	move $a1, $s3
	jal powerOfTwo
	add $s0, $s0, $v0 

# update counters   
skip1:
	srl $t2, $t2, 1
	sub $s3, $s3, 1
	add $s1, $s1, 1
	add $s2, $s2, 1
	# if bit counter is at 5, goto incChar
	beq $s1, 5, incChar
	# else continue reading the current character
	j skip2

# print current character and reset for next character
incChar:
	la $t5,	chars
	add $t5, $t5, $s0
	lb $a0, ($t5)
	li $v0, 11
	syscall
	li $s0, 0
	li $s1, 0
	li $s3, 4

# check for end of byte
skip2:
	#if end of byte, goto incByte
	beq $s2, 8, incByte
	j skip3

# reset byte and goto next one
incByte:
	li $s2, 0
	add $t0, $t0, 1
	j loop

# return to checkBit
skip3:
	j checkBit

# exits
exit:
	li $v0, 10
	syscall


#######################################
#   PowerOfTwo:                       #
#       return 2^n                    #
#######################################
powerOfTwo:
	beqz $a1, returnOne
	sub $a1, $a1, 1
	li $t7, 2
powerLoop:
	beqz $a1, returnPowerLoop
	mul $t7, $t7, 2
	sub $a1, $a1, 1
	j powerLoop
returnOne:
	li $t7, 1
returnPowerLoop:
	move $v0, $t7
	jr $ra
#######################################