// Caden Dengel
// 2/25/2024
// 
// main():
//   the program ensures the file opens and closes properly. it reads the file
//   line by line, ensuring the current line is not empty before checking if
//   the number is a triangular number. if it is, the program adds the index
//   and word to the map. after reading the entire file, the program outputs
//   the words in the map.

#include <iostream>
#include <fstream>
#include <sstream>
#include <map>

int main() {
	// initialize the file stream, the triangular number check int, and the map
	std::ifstream fin;
	fin.open("coding_qual_input.txt");
	if (!fin) {
		std::cerr << "File not opened\n";
		return 1;
	}
	int m = 0;
	std::map<int, std::string> words;

	// read the file line by line
	while (!fin.eof()) {
		std::string str;
		std::getline(fin, str);

		// test if the current line is a triangular number
		if (str != "") { // ensure the line is not empty
			m = 1 + 8 * stoi(str);
			if ((int)sqrt(m) * (int)sqrt(m) == m) {
				std::string temp = str;
				int i = 0;

				// delete everything before the word
				while (temp[i] != ' ' && temp[i] != '\0')
					++i;
				temp.erase(0, i + 1);

				// insert the word into the map
				words[stoi(str)] = temp;
			}
		}
	}

	// output the words
	for (const auto& m : words)	
		if (m.second != "") 
			std::cout << m.second << ' ';

	fin.close();

	return 0;
}