/** 
 * 避免耗时运算
 * 1. 避免“昂贵”运算的优化技术被称为强度消减（Strength Reduction）
*/

#include <iostream>
#include <cstdlib>
#include <ctime>
#include <cmath>

#define random(a,b) (rand()%(b-a+1)+a)

#define N 100000

using namespace std;

const double tt = 0.5;

int main(int argc, char* argv[]) {
    srand((int)time(NULL));
    // [[iL, iR, iU, iO, iS, iN],
    //  [iL, iR, iU, iO, iS, iN],
    //  ...
    // ]    
    static int_fast8_t is[N][6] = {0};

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < 6; j++) {
            is[i][j] = (random(0, 1) == 0)?-1:1;
        }
    }

    for (int i = 0; i < N; i++) {
        double edelz = (double)(is[i][0] + is[i][1] + is[i][2] + is[i][3] + is[i][4] + is[i][5]);
        double BF = 0.5 * (1.0 + tanh(edelz / tt));
    }
}