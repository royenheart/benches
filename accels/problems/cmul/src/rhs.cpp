#include <cmath>
#include "rhs.h"

void matA(unsigned int &i, unsigned int &j, double &value) {
    value = std::sin(i + 2 * j);
    // value = 1;
}

void matB(unsigned int &i, unsigned int &j, double &value) {
    value = std::cos(3 * i + j);
    // value = 1;
}