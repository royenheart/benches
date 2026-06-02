#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
    std::cout << sizeof(char) << std::endl;
    std::cout << sizeof(wchar_t) << std::endl;
    wchar_t c = '你';
    std::cout << "wchar_t c size: " << sizeof(c) << ";c content: " << c << std::endl;
    std::cout << "Alignment of int: " << alignof(int) << " bytes" << std::endl;
    std::cout << "Alignment of double: " << alignof(double) << " bytes" << std::endl;
    std::cout << "Alignment of char: " << alignof(char) << " bytes" << std::endl;
    std::string s = "我是谁，到达。单独的，";
    std::cout << sizeof(std::string) << std::endl;
    std::cout << s.size() * sizeof(char) << std::endl;
}