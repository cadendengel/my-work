/*******************************************************************************
Happy Prime Finder v3
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
#include <omp.h>
int getNext(int n) {
	int totalSum = 0;
	while (n > 0) {
		int d = n >= 10 ? n % 10 : n;
		n *= .1f;
		totalSum += d * d;
	}
	return totalSum;
}
bool floydCycle(int n) {
	int s = n, f = getNext(n);
	while (s != f) {
		s = getNext(s);
		f = getNext(getNext(f));
	}
	return f == 1;
}
void sieveOfEratosthenes() {
	int c = 0;
	std::vector<bool> is_prime(1000001, true);
	for (int i = 2; i * i <= 1000000; i++) {
		int j = i * i;
		if (is_prime[i] && j <= 1000000) {
			for (j; j <= 1000000; j += i) {
				is_prime[j] = false;
			}
		}
	}
	#pragma omp parallel shared(c)
	{
	#pragma omp for reduction(+:c)
		for (int i = 2; i < 1000001; i++) {
			if (is_prime[i]) {
				if (floydCycle(i)) {
					c++;
				}
			}
		}
	}
	std::cout << c;
}
int main() {
	sieveOfEratosthenes();
	return 0;
}