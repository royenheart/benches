/**

给定一个 n × n 的二维矩阵 matrix 表示一个图像。请你将图像顺时针旋转 90 度。

你必须在 原地 旋转图像，这意味着你需要直接修改输入的二维矩阵。请不要
使用另一个矩阵来旋转图像。

示例 1：

输入：matrix = [[1,2,3],[4,5,6],[7,8,9]]
输出：[[7,4,1],[8,5,2],[9,6,3]]
示例 2：

输入：matrix = [[5,1,9,11],[2,4,8,10],[13,3,6,7],[15,14,12,16]]
输出：[[15,13,2,5],[14,3,4,1],[12,6,8,9],[16,7,10,11]]

提示：

n == matrix.length == matrix[i].length
1 <= n <= 20
-1000 <= matrix[i][j] <= 1000

*/

#include <bench/competitive/problem.hpp>

#include <vector>

using namespace std;

class Solution {
  public:
    void rotate(vector<vector<int>>& matrix) {
        size_t n = matrix.size();
        for (auto iter = 0; iter < n / 2; iter++) {
            for (auto iner_iter = 0; iner_iter < (n - 2 * iter) - 1;
                 iner_iter++) {
                size_t x = 1 + iter;
                size_t y = 1 + iter + iner_iter;
                size_t next_x = y;
                size_t next_y = n - x + 1;
                int current = matrix[x - 1][y - 1];
                int tmp = matrix[next_x - 1][next_y - 1];

                // cout << "[" << x << "," << y << "]" << ",";

                // cout << "[" << next_x << "," << next_y << "]";

                // cout << ":<" << current << "," << tmp << ">,";

                for (int rotate = 0; rotate < 4; rotate++) {
                    matrix[next_x - 1][next_y - 1] = current;
                    current = tmp;
                    x = next_x;
                    next_x = next_y;
                    next_y = n - x + 1;
                    tmp = matrix[next_x - 1][next_y - 1];

                    // cout << "[" << next_x << "," << next_y << "]";
                    // cout << ":<" << current << "," << tmp << ">,";
                }

                // cout << endl;
            }
        }
    }
};

vector<vector<int>> sample1() {
    Solution sol;
    auto q = vector<vector<int>>({{1, 2, 3}, {4, 5, 6}, {7, 8, 9}});
    sol.rotate(q);
    return q;
}

vector<vector<int>> sample2() {
    Solution sol;
    auto q = vector<vector<int>>(
        {{5, 1, 9, 11}, {2, 4, 8, 10}, {13, 3, 6, 7}, {15, 14, 12, 16}});
    sol.rotate(q);
    return q;
}

int answer() {
    cout << sample1() << "\n";
    cout << sample2() << "\n";
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)
