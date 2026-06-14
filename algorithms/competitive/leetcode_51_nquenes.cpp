/**

按照国际象棋的规则，皇后可以攻击与之处在同一行或同一列或同一斜线上的棋子。

n 皇后问题 研究的是如何将 n 个皇后放置在 n×n
的棋盘上，并且使皇后彼此之间不能相互攻击。

给你一个整数 n ，返回所有不同的 n 皇后问题 的解决方案。

每一种解法包含一个不同的 n 皇后问题 的棋子放置方案，该方案中 'Q' 和 '.'
分别代表了皇后和空位。

示例 1：

输入：n = 4
输出：[[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]
解释：如上图所示，4 皇后问题存在两个不同的解法。
示例 2：

输入：n = 1
输出：[["Q"]]

提示：

1 <= n <= 9

*/

#include <bench/competitive/problem.hpp>

#include <string>
#include <unordered_set>
#include <vector>

using namespace std;

// 对角线映射，且由于一步一步来点，不会有皇后处于同一个对焦线上，也就是对角线
// visited 不会有冲突。
// visited 的含义是坐标轴上的占据，分三个坐标轴
class Solution {
  public:
    void level_q(int level, unordered_set<int>& visited,
                 unordered_set<int>& left_visited,
                 unordered_set<int>& right_visited, vector<string>& sol) {
        for (int j = 0; j < n; j++) {
            if ((visited.find(j) == visited.end()) &&
                (left_visited.find(j + level) == left_visited.end()) &&
                (right_visited.find(n - j - 1 + level) ==
                 right_visited.end())) {
                if (level == n - 1) {
                    auto mystr = blank_str;
                    mystr[j] = 'Q';
                    sol.push_back(mystr);
                    results.push_back(sol);
                    sol.pop_back();
                } else {
                    visited.insert(j);
                    left_visited.insert(j + level);
                    right_visited.insert(n - j - 1 + level);

                    auto mystr = blank_str;
                    mystr[j] = 'Q';
                    sol.push_back(mystr);
                    level_q(level + 1, visited, left_visited, right_visited,
                            sol);
                    sol.pop_back();

                    visited.erase(j);
                    left_visited.erase(j + level);
                    right_visited.erase(n - j - 1 + level);
                }
            }
        }
    }

    vector<vector<string>> solveNQueens(int n) {
        this->n = n;
        blank_str = string(n, '.');
        unordered_set<int> init_visited;
        unordered_set<int> left_visited;
        unordered_set<int> right_visited;
        vector<string> sol;
        level_q(0, init_visited, left_visited, right_visited, sol);
        return results;
    }

  private:
    string blank_str;
    int n;
    vector<vector<string>> results;
};

vector<vector<string>> sample1() {
    Solution sol;
    return sol.solveNQueens(4);
}

vector<vector<string>> sample2() {
    Solution sol;
    return sol.solveNQueens(1);
}

int answer() {
    cout << sample1() << "\n";
    cout << sample2() << "\n";
    return 0;
}

BENCH_COMPETITIVE_MAIN(answer)
