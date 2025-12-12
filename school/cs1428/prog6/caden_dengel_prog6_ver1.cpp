/*******************************************************************************
Happy Prime Finder v1
Caden Dengel
CS1428.H01
Dr. Zillian Zong
Due 11/29/2-22
Written 11/28/2022
This program finds the number of happy primes between 1 and 1,000,000
It has no dependencies apart from the includes.
******************************************************************************/
#include <vector>
#include <iostream>
// gets the next value for the floyd cycle
int getNext(int n) {
	int totalSum = 0;
	while (n > 0) {
		// fast modulo
		int d = n >= 10 ? n % 10 : n;
		// multiply instead of divide for speed and efficiency
		n *= .1f;
		totalSum += d * d;
	}
	return totalSum;
}
// floyd's cycle
// algorithm that determines if a number is happy
bool floydCycle(int n) {
	int s = n, f = getNext(n);
	while (s != f) {
		s = getNext(s);
		f = getNext(getNext(f));
	}
	return f == 1;
}
// sieve of eratosthenes
// algorithm that determines if a number is prime
void sieveOfEratosthenes() {
	// count of happy primes
	int c = 0;
	// i used bool vectors because bools are 1 byte
	// making them the fastest and most efficient
	// even despite including <vector>
	std::vector<bool> is_prime(1000001, true);
	for (int i = 2; i * i <= 1000000; i++) {
		int j = i * i;
		// these nested statements ensure i has not already been
		// marked composite, that the number being marked composite
		// is less than the target number (1000000) and also that
		// all multiples j of int i are marked composite (false)
		if (is_prime[i] && j <= 1000000) {
			for (j; j <= 1000000; j += i) {
				is_prime[j] = false;
			}
		}
	}
	// for each prime...
	for (int i = 2; i < 1000001; i++) {
		if (is_prime[i]) {
			// determine if prime is unhappy...
			if (floydCycle(i)) {
				// and add to the counter
				c++;
			}
		}
	}
	std::cout << c;
}
int main() {
	sieveOfEratosthenes();
	return 0;
}