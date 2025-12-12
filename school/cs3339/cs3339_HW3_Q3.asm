.data
	prompt: .asciiz "Enter a float: \n"
	float1: .float 6.0
	float2: .float 120.0
.text
	# prompt user
	li $v0, 4
	la $a0, prompt
	syscall
	
	# read x from user into $f0 then move to $f12
	li $v0, 6
	syscall
	
	mov.s $f12, $f0
	
	
	# compute x^3 in $f1
	# x^3
	mul.s $f1, $f0, $f0
	mul.s $f1, $f1, $f0
	# load 6.0 into $f2, then divide $f1 by $f2
	# (x^3) / 6.0
	l.s $f2, float1
	div.s $f1, $f1, $f2
	# subtract $f1 from $f12
	# x - [ (x^3) / 6.0 ]
	sub.s $f12, $f12, $f1
	
	
	# compute x^5 in $f1
	# x^5
	mul.s $f1, $f0, $f0
	mul.s $f1, $f1, $f0
	mul.s $f1, $f1, $f0
	mul.s $f1, $f1, $f0
	# load 120.0 into $f2, then divide $f1 by $f2
	# (x^5) / 120.0
	l.s $f2, float2
	div.s $f1, $f1, $f2
	# add $f1 and $f12
	# { x - [ (x^3) / 6.0 ] } + [ (x^5) / 120.0 ]
	add.s $f12, $f12, $f1
	
	
	# return $f12 / sin(x)
	li $v0, 2
	syscall
	
	# exit
	li $v0, 10
	syscall